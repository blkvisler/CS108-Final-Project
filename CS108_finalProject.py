#!/usr/bin/python
#
# AUTHOR: Ben Kvisler (bkvisler@bu.edu)
# DUE DATE: 12/10/14
# FILE: CS108_finalProject.py
# URL: http://cs-webapps.bu.edu/cs108/bkvisler/CS108_finalProject.py
# DESCRIPTION: CS108 Final Project. A program that helps users find, update, add, and
#  comment on websites/resources that show online design inspiration (from website
#  design to mobile UI). Users can also search for content under topics
#  such as "Design Inpsiration" and they can submit feedback on the website.
# NOTE: "website" and "resource" are used interchangeably
#
# FEATURES:
#  Homepage with menu of options
#  Show all resources (with pictures and links to respecitive sites)
#  Show resources by specified topic
#  View website/resource page along with comments
#  View comments in reverse chronilogical order for specified website
#  Add a comment for specified website
#  Add a new resource
#  Update parts of the website information with a form that is prefilled with
#   current content
#  Be notified if you didn't input all information for Add or Update A Resource or Comment
#  Be notified if update or additions were successful
#  Feedback submission form
#
# SQL TABLES AND VARIABLES
# websites
#  siteID, siteTitle, url, description, topic, pictureURL, logoURL
# comments
#  commentID, siteID, time, fullname, comment


import MySQLdb as db
import time
import cgi
import cgitb; cgitb.enable()
import smtplib

print("Content-Type: text/html")
print("") # Blank line


################################################################################
def getConnectionAndCursor():
    """
    This function will connect to the database and return the
    Connection and Cursor objects.
    """ 
    # connect to the MYSQL database
    conn = db.connect(host="localhost",
                      user="bkvisler",
                      passwd="8353",
                      db="bkvisler")

    cursor = conn.cursor()
    return conn, cursor


################################################################################
def doHTMLHead(title):

    print("""
    <html>

    <!-- HEAD -->
    <head>
    <link href="http://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet" type="text/css">

    <!-- STYLE -->
    <style>
        .header {
            background-color: rgba(41, 128, 185,.4);
            top:0px;
            margin-top: -25px;
            }
        .footer {
            background-color: rgba(41, 128, 185,.4);
            padding-bottom: 10px;
            align: center;
            }
        .bodydiv {
            background-color: rgba(41, 128, 185,.3);
            align:center;
            }
        #title {
            text-decoration:none;
            }
        /* body {background-image:url("bg.png");} */
        /* body {background-color:rgb(47, 197, 246);} */
        body {
            background-image: url("Triangles.jpg");
            background-position: top center;
            background-attachment: fixed;
            }
        h1 {
            font-family:"Lato", "Courier", "Times New Roman";
            color:rgb(241, 196, 15);
            letter-spacing: 10px;
            padding-top: 15px;
            margin-bottom: -10px;
            }
        h3 {
            font-family:"Lato", "Courier", "Times New Roman";
            color:rgb(44, 62, 80);
            }
        h2, p, label {
            font-family:"Lato", "Courier", "Times New Roman";
            color:rgb(236, 240, 241);
            }
        a:link {color: #3BB9FF;}
        a:visited {color: #F1C40F;}
        a:hover {color: #2ECC71;}
        a:active {color: #ECF0F1;}
        table {
            font-family:"Courier", serif;
            border-color: rgb(47, 197, 246);
            color:rgb(236, 240, 241);
            text-align:center;
            max-width:1024px;
            }
        input[type="submit"], input[type="reset"], input[type="button"] {
            font-family: "Lato", "Courier", "Times New Roman";
            font-size: 17px;
            color: rgb(236, 240, 241);
            border-radius: 10px;
            height: 35px;
            border: none;
            background: rgb(46, 204, 113);
            margin: 5px;
            }
        input[type="submit"]:hover, input[type="reset"]:hover, input[type="button"]:hover {
            background: rgb(39, 174, 96);
            color:rgb(241, 196, 15);
            }
        select {
            font-family: "Lato", "Courier", "Times New Roman";
            font-size: 15px;
            color: rgb(236, 240, 241);
            width:200px;
            height:25px;
            border: none;
            background: rgb(46, 204, 113);
            margin: 5px;
            }
        select:hover {
            color:rgb(241, 196, 15);
            background: rgb(39, 174, 96);
            }
    </style>

    <!-- HEAD TITLE -->
    <title>%s</title>    
    </head>

    <!-- BODY -->
    <body align="center">
    <div class="bodydiv">

    <!-- HEADER AND MAIN TITLE -->
    <div class="header">
    <a id="title" href="./CS108_finalProject.py">
    <h1>ONLINE DESIGN INSPIRATION</h1>
    </a>

    <!-- SITE DESCRIPTION -->
    <h3><i>This is a website dedicated to bringing you quality resources on web design including
    inpirational material, templates, and tutorials.<br>
    You can view all the resources or sort by them topic, add and update resources, and
    view and add comments.</i></h3>
    <hr>
    </div>
    """ % (title))


################################################################################
def doHTMLTail():

    ## Link back to the main page along with date the page was generated
    print("""
    <!-- FOOTER -->
    <div class="footer">
    <hr>
    <p><a href="./CS108_finalProject.py">Return to Home Page</a> |
    <a href="./CS108_finalProject.py?showFeedbackForm=x">Submit Feedback</a><br>
    Page Generated on %s<br>
    Created by <a href="http://benkvisler.com">Ben Kvisler</a> for Professor Aaron
    Steven's CS108</p>
    </div>

    </div>
    </body>
    </html>

    """ % time.ctime())


################################################################################
def debugFormData(form):
    """
    A helper function which will show us all of the form data that was
    sent to the server in the HTTP form.
    """
    
    print("""
    <h2>DEBUGGING INFORMATION</h2>
    <p>
    Here are the HTTP form data:
    """)
    print("""
    <table border=1>
        <tr>
            <th>key name</th>
            <th>value</th>
        </tr>
    """)
    
    # form behaves like a python dict
    keyNames = form.keys()
    # note that there is no .values() method -- this is not an actual dict

    ## use a for loop to iterate all keys/values
    for key in keyNames:

        ## discover: do we have a list or a single MiniFieldStorage element?
        if type(form[key]) == list:

            # print out a list of values
            values = form.getlist(key)
            print("""
        <tr>
            <td>%s</td>
            <td>%s</td>
        </tr>
            """ % (key, str(values)))

        else:
            # print the MiniFieldStorage object's value
            value = form[key].value
            print("""
        <tr>
            <td>%s</td>
            <td>%s</td>
        </tr>
            """ % (key, value))
        
    print("""
    </table>
    <h3>End of HTTP form data</h3>
    <hr>
    """)

## end: def debugFormData(form)
################################################################################


################################################################################
def getAllWebsites():
    """
    Middleware function to get all websites' information from the websites table.
    Returns a list of tuples of (siteID, siteTitle, url, description, topic,
    pictureURL, logoURL).
    """

    ## Connect to database
    conn, cursor = getConnectionAndCursor()

    ## SQL to retreive website database content
    sql = """
    SELECT siteID, siteTitle, url, description, topic, pictureURL, logoURL
    FROM websites
    """

    ## Execute the query
    cursor.execute(sql)

    ## Get the data from the database
    websiteData = cursor.fetchall()

    ## Clean up and close connection
    conn.close()
    cursor.close()

    return websiteData

## end: def getAllWebsites()


################################################################################
def getAllWebsitesByTopic(topic):
    """
    Middleware function to get all websites' information given a selected topic.
    """

    ## Connect to database
    conn, cursor = getConnectionAndCursor()

    ## SQL to retreive website database content
    sql = """
    SELECT siteID, siteTitle, url, description, topic, pictureURL, logoURL
    FROM websites
    WHERE topic = %s
    """

    ## Execute the query
    parameters = (topic, )
    cursor.execute(sql, parameters)

    ## Get the data from the database
    websiteData = cursor.fetchall()

    ## Clean up and close connection
    conn.close()
    cursor.close()

    return websiteData

## end: def getAllWebsitesByTopic()


################################################################################
def getOneWebsite(siteID):
    """
    Middleware function to get a selected website's information.
    """

    ## Connect to database
    conn, cursor = getConnectionAndCursor()

    ## SQL to retreive website database content
    sql = """
    SELECT siteID, siteTitle, url, description, topic, pictureURL, logoURL
    FROM websites
    WHERE siteID = %s
    """

    ## Execute the query
    parameters = (siteID, )
    cursor.execute(sql, parameters)

    ## Get the data from the database
    websiteData = cursor.fetchall()

    ## Clean up and close connection
    conn.close()
    cursor.close()

    return websiteData

## end: def getOneWebsite()


################################################################################
def showOneWebsite(websiteData):
    """
    Presentation layer function to display a single website's information.
    Will be shown along with respecitive comments (showComments() function).
    """

    ## Show website information

    # Unpack the data
    (siteID, siteTitle, url, description, topic, pictureURL, logoURL) = websiteData[0]

    print("""
    <div align="center">

    <!-- SITE TITLE WITH LINK -->
    <h2><a href="%s">%s</a></h2>

    <!-- UPDATE WEBSITE OPTION -->
    <form>
        <input type="hidden" name="siteID" value="%s">
        <input type="submit" name="showUpdateWebsiteForm" value="Update Resource">
    </form>

    <!-- WEBSITE INFORMATION HEADER -->
    <h2>Website Information</h2>
    
    <!-- SITE LOGO -->
    <img style="max-width:150px" src="%s">
    
    <!--SITE DESCRIPTION -->
    <p style="max-width:450px">%s</p>
    
    <!-- SITE SCREENSHOT -->
    <img style="max-width:450px" src="%s">
    
    </div>
    <br>
    """ % (url, siteTitle, siteID, logoURL, description, pictureURL))

## end: def showOneWebsite()


################################################################################
def showWebsiteData(websiteData):
    """
    Presentation layer function to display the website list and information.
    """

    ## Length of website data (i.e. number of resources)
    ## Accounting for singular and plural of "resource(s)"
    lengthDescription = ""
    if len(websiteData) != 1:
        lengthDescription = "Found " + str(len(websiteData)) + " Resources"
    else:
        lengthDescription = "Found " + str(len(websiteData)) + " Resource"
        
    
    ## Show website database information

    ## Start table
    print("""
    <h2>Resources</h2>
    <p>%s</p>
    <!-- TABLE OF WEBSITE DATA -->
    <table border="1px" align="center">
    <tr>
        <th>Site ID</th>
        <th>Site Title</th>
        <th>Description</th>
        <th>Topic</th>
        <th>Site Screenshot</th>
        <th>Site Logo</th>
        <th>Extra</th>
    </tr>
    """ % lengthDescription)
          
    ## Iterate through websiteData to display the website list in a table
    for website in websiteData:
        # Unpack data for each website
        (siteID, siteTitle, url, description, topic, pictureURL, logoURL) = website

        print("""
        <!-- CONTENT OF THE WEBSITE DATA -->
        <tr>
            <td>%s</td>
            <td><a href="%s">%s</a></td>
            <td>%s</td>
            <td>%s</td>
            <td><img style="max-width:250px" src="%s"</td>
            <td><img style="max-width:100px" src="%s"></td>
            <td>
                <form>
                    <input type="hidden" name="siteID" value="%s">
                    <input type="submit" name="showCommentary" value="Show Commentary">
                </form>
                <form>
                    <input type="hidden" name="siteID" value="%s">
                    <input type="submit" name="showUpdateWebsiteForm" value="Update Resource">
                </form>
            </td>
        </tr>
        """ % (siteID, url, siteTitle, description, topic, pictureURL, logoURL, siteID, siteID))

    ## Close table
    print("""
    </table>
    """)

    ## Include the Add A Resource option in case a users wants to do that
    print("""
    <!-- ADD A WEBSITE OPTION -->
    <h2>Don't See Something Interesting? Add A Resource:</h2>
    <form>
        <input type="submit" name="showAddAWebsiteForm" value="Add A Resource">
    </form>
    """)

## end: def showWebsiteData()


################################################################################
def getComments(siteID):
    """
    Middleware function to get comments in reverse chronological order
    from database for a choosen website.
    """

    ## Connect to database
    conn, cursor = getConnectionAndCursor()

    ## SQL to retreive comments for choosen website in reverse chronological order
    sql = """
    SELECT commentID, siteID, time, fullname, comment
    FROM comments
    WHERE siteID = %s
    ORDER BY commentID DESC
    """

    ## Execute the query
    parameters = (siteID, )
    cursor.execute(sql, parameters)

    ## Get the data from the database
    comments = cursor.fetchall()

    ## Clean up and close connection
    conn.close()
    cursor.close()

    return comments

## end: def getComments()


################################################################################
def showComments(comments, siteID):
    """
    Presentation layer function to display comments for the choosen website.
    Also includes a form to add a comment.
    """

    ## Show website information and respective commentary along with
    ##  Add Comment form

    ## Add a comment form
    print("""
    <!-- ADD A COMMENT FORM -->
    <h2>Add A Comment</h2>
    <form>

    <table align="center">
    <!-- FULL NAME FIELD -->
    <tr>
        <td><label>First and Last Name</label></td>
        <td><input type="text" name="fullname" size="30px"></td>
    </tr>

    <!-- COMMENT FIELD -->
    <tr>
        <td><label>Comment</label></td>
        <td><input type="text" name="comment" size="30px"></td>
    </tr>
    
    <tr>
        <td colspan="2">
        <input type="submit" name="addComment" value="Add Your Comment">
        <input type="reset" name="reset" value="Reset Form">
        </td>
    </tr>
    
    </table>

    <!-- HIDDEN SITEID FIELD -->
    <input type="hidden" name="siteID" value="%s">
    </form>
    """ % (siteID))


    ## Beginning of the Comments table display
    print("""
    <!-- COMMENTARY -->
    <h2>Comments</h2>
    <table border="1px" align="center">
    <tr>
        <th>Time</th>
        <th>Name</th>
        <th>Comment</th>
    </tr>
    """)
          
    ## Iterate through comments to display them in the table
    # They will display in reverse chronological order because of the SQL
    for comment in comments:
        (commentID, siteID, time, fullname, comment) = comment

        print("""
        <!-- ALL THE COMMENTS -->
        <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
        </tr>
        """ % (time, fullname, comment))

    ## Close table
    print("""
    </table>
    """)

## end: def showComments()


################################################################################
def showHomepage():
    """
    Presentation layer to show the homepage and primary functions. Primary
    functions include showing the main website list, showing the websites by topic,
    and add a new website to the list.
    """

    ## HTML for the primary functions
    print("""
    <!-- SHOW LIST OF RESOURCES -->
    <h2>Show All Resources<h2>
    <form>
        <input type="submit" name="showWebsiteData" value="Show Resource List">
    </form>


    <!-- SHOW RESOURCES BY TOPIC -->
    <h2>Show All Resources by Topic</h2>
    <form>
        <label>Choose Topic to Search Resources</label><br>
        <select name="topic">
            <option value="Design Inspiration">Design Inspiration</option>
            <option value="Templates">Templates</option>
            <option value="Tutorials">Tutorials</option>
        </select><br>
        <input type="submit" name="showWebsitesByTopic" value="Show Resources By Topic">
    </form>

    
    <!-- ADD A WEBSITE -->
    <h2>Add A Resource</h2>
    <form>
        <input type="submit" name="showAddAWebsiteForm" value="Add A Resource">
    </form>
    """)

## end: def showHomepage():


################################################################################
def showAddAWebsiteForm():
    """
    Presentation layer that shows an HTML form to get a new resource/website's info.
    """

    ## Add A New Website/Resource Form
    print("""
    <!-- ADD A NEW WEBSITE FORM -->
    <h2>Enter New Website Information</h2>
    <form>
    <table align="center">
    
    <tr>
        <td colspan="2"><label>Please Make Sure to Fill Out All Form Boxes</label></td>
    </tr>

    <!-- SITE TITLE FIELD -->
    <tr>
        <td><label>Site Title:</label></td>
        <td><input type="text" name="siteTitle" size="30px"></td>
    </tr>

    <!-- URL FIELD -->
    <tr>
        <td><label>URL:</label></td>
        <td><input type="text" name="url" size="30px"></td>
    </tr>

    <!-- DESCRIPTION FIELD -->
    <tr>
        <td><label>Description:</label></td>
        <td><input type="text" name="description" size="30px"></td>
    </tr>

    <!-- TOPIC FIELD -->
    <tr>
        <td><label>Topic:</label>
        <td>
        <select name="topic">
            <option value="Design Inspiration">Design Inspiration</option>
            <option value="Templates">Templates</option>
            <option value="Tutorials">Tutorials</option>
        </select>
        </td>
    </tr>

    <!-- WEBSITE SCREENSHOT URL FIELD -->
    <tr>
        <td><label>Website Screenshot (Image URL):</label>
        <td><input type="text" name="pictureURL" size="30px"></td>
    </tr>

    <!-- WEBSITE LOGO URL FIELD -->
    <tr>
        <td><label>Website Logo (Image URL):</label></td>
        <td><input type="text" name="logoURL" size="30px"></td>
    </tr>

    <tr>
        <td colspan="2">
        <input type="submit" name="addAWebsite" value="Add New Website">
        <input type="reset" name="reset" value="Reset Form">
        <input type="submit" name="cancel" value="Cancel">   
        </td>
    </tr>
    
    </table>
    </form>
    """)

## end: def showAddAWebsiteForm():


################################################################################
def addAWebsite(siteTitle, url, description, topic, pictureURL, logoURL):
    """
    Middleware function to add the new website/resource to the database. Parameters
    are the retreived from the form fields of showAddAWebsiteForm.
    """

    ## Connect to database
    conn, cursor = getConnectionAndCursor()


    ## Get max siteID SQL then find the next ID
    maxSiteIDSQL = """
    SELECT max(siteID)
    FROM websites
    """

    cursor.execute(maxSiteIDSQL)
    siteID = cursor.fetchone()
    nextID = int(siteID[0])+1

    
    ## SQL to add a new website to the database
    ##  (siteID, siteTitle, url, description, topic, pictureURL, logoURL)
    sql = """
    INSERT INTO websites
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    ## Execute the query
    parameters = (nextID, siteTitle, url, description, topic, pictureURL, logoURL)
    cursor.execute(sql, parameters)

    
    ## Clean up and close connection
    conn.commit()
    conn.close()
    cursor.close()

    ## Return rowcount to notify user of (un)succesful attempt
    rowcount = cursor.rowcount
    return rowcount

## end: def addAWebsite():


################################################################################
def updateWebsiteForm(websiteData):
    """
    Presentation layer that shows an HTML form to update new website's info.
    """

    ## Unpack current resource data
    (siteID, siteTitle, url, description, topic, pictureURL, logoURL) = websiteData[0]

    ## Show form partially filled out with some fields left unchanablge
    print("""
    <!-- UPDATE WEBSITE FORM -->
    <h2>Update Website Information</h2>
    <form>
    <table align="center">

    <!-- SITE TITLE FIELD -->
    <tr>
        <td><label>Site Title:</label></td>
        <td>%s</td>
    </tr>

    <!-- URL FIELD -->
    <tr>
        <td><label>URL:</label></td>
        <td><input type="text" name="url" value="%s" size="30px"></td>
    </tr>

    <!-- DESCRIPTION FIELD -->
    <tr>
        <td><label>Description:</label></td>
        <td><input type="text" name="description" value="%s" size="30px"></td>
    </tr>

    <!-- TOPIC FIELD -->
    <tr>
        <td><label>Topic:</label>
        <td>%s</td>
    </tr>

    <!-- WEBSITE SCREENSHOT URL FIELD -->
    <tr>
        <td><label>Website Screenshot (Image URL):</label>
        <td><input type="text" name="pictureURL" value="%s" size="30px"></td>
    </tr>

    <!-- WEBSITE LOGO URL FIELD -->
    <tr>
        <td><label>Website Logo (Image URL):</label></td>
        <td><input type="text" name="logoURL" value="%s" size="30px"></td>
    </tr>

    <tr>
        <td colspan="2"><input type="submit" name="updateWebsite" value="Update Website">
        <input type="reset" name="reset" value="Reset Form">
        <input type="submit" name="cancel" value="Cancel"></td>
    </tr>

    </table>
    <!-- HIDDEN SITEID FIELD -->
    <input type="hidden" name="siteID" value="%s">
    </form>
    """ % (siteTitle, url, description, topic, pictureURL, logoURL, siteID))

## end: def updateWebsiteForm():


################################################################################
def updateWebsite(siteID, url, description, pictureURL, logoURL):
    """
    Middleware function to update a website/resource in the database
    """
    
    ## Connect to database
    conn, cursor = getConnectionAndCursor()
    
    ## SQL to add a new website to the database
    ##  (siteID, siteTitle, url, description, topic, pictureURL, logoURL)
    sql = """
    UPDATE websites
    SET url=%s, description=%s, pictureURL=%s, logoURL=%s
    WHERE siteID=%s
    """

    ## Execute the query
    parameters = (url, description, pictureURL, logoURL, siteID)
    cursor.execute(sql, parameters)
    
    ## Clean up and close connection
    conn.commit()
    conn.close()
    cursor.close()

    ## Return rowcount to notify user of (un)succesful attempt
    rowcount = cursor.rowcount
    return rowcount

## end: def updateWebsite():


################################################################################
def addComment(siteID, fullname, comment):
    """
    Middleware function to add the new comment. Parameters include those from the
    form of the showComments() function.
    """

    ## Connect to database
    conn, cursor = getConnectionAndCursor()

    ## Getting Time
    tm = time.localtime()
    timestamp = '%04d-%02d-%02d %02d:%02d:%02d' % tm[0:6]
    
    ## Get max commentID SQL then find the next ID
    maxCommentIDSQL = """
    SELECT max(commentID)
    FROM comments
    """

    cursor.execute(maxCommentIDSQL)
    commentID = cursor.fetchone()
    nextID = int(commentID[0])+1

    
    ## SQL to add a new comment to the comments table for a specific website
    # (commentID, siteID, time, fullname, comment)
    sql = """
    INSERT INTO comments
    VALUES (%s, %s, %s, %s, %s)
    """

    ## Execute the query
    parameters = (nextID, siteID, timestamp, fullname, comment)
    cursor.execute(sql, parameters)
    
    ## Clean up and close connection
    conn.commit()
    conn.close()
    cursor.close()

    ## Return rowcount to notify user of (un)succesful attempt
    rowcount = cursor.rowcount
    return rowcount

## end: def addComment():


################################################################################
def showFeedbackForm():
    """
    Presentation layer that shows an HTML form to request feedback on the website.
    Feedback is sent to the webmaster.
    """

    ## Feedback Form :: Partially blank feedback forms are accepted so as to solicit more feedback
    print("""
    <h2>Feedback Submission Form</h2>

    <form>
    <table align="center">

    <tr>
        <td colspan="2">
        <label>Please Make Sure To Fill Out All Form Fields</label>
        </td>
    </tr>
    
    <tr>
        <td>First Name:</td>
        <td align="left"><input type="text" name="firstname" required></td>
    </tr>
    
    <tr>
        <td>Last Name:</td>
        <td align="left"><input type="text" name="lastname" required></td>
    </tr>
    
    <tr>
        <td>Email:</td>
        <td align="left"><input type="text" name="email" required></td>
    </tr>
    
    <tr>
        <td>Feedback:</td>
        <td align="left"><input type="text" name="feedback" required></td>
    </tr>

    <tr>
        <td>Rating:</td>
        <td align="left">
            <input type="radio" name="rating" value="awesome">
            <label>Awesome</label><br>
            <input type="radio" name="rating" value="great">
            <label>Great</label><br>
            <input type="radio" name="rating" value="okay">
            <label>Okay</label><br>
            <input type="radio" name="rating" value="needsWork">
            <label>Needs Work</label>
        </td>
    </tr>

    <tr>
        <td>Best Features:</td>
        <td align="left">
            <input type="checkbox" name="vastResourceCollection" value="vastResourceCollection">
            <label>Vast Resource Collection</label><br>
            <input type="checkbox" name="addingResources" value="addingResources">
            <label>Adding Resources</label><br>
            <input type="checkbox" name="viewingCommentary" value="viewingCommentary">
            <label>Viewing Commentary</label><br>
            <input type="checkbox" name="sortingResroucesByTopic" value="sortingResroucesByTopic">
            <label>Sorting Resrouces by Topic</label>
        </td>
    </tr>

    <tr>
        <td colspan="2">
            <input type="submit" name="submitFeedback" value="Submit Feedback">
            <input type="reset" name="reset" value="Reset Form">
            <input type="button" name="cancel" value="Cancel" onclick="window.location='./CS108_finalProject.py'">
        </td>
    </tr>
    
    </table>
    </form>
    """)

## end: def showFeedbackForm():


################################################################################
def createEmail(firstname, lastname, email, feedback, rating, vastResourceCollection, addingResources, viewingCommentary, sortingResroucesByTopic):
    """
    Create the email usign the feedback provided from the feedback form
    """

    msg = """
    Feedback\n
    First Name = %s
    Last Name = %s
    Email = %s
    Feedback = %s
    Rating = %s
    Features
    Resource Collection = %s
    Adding Resources = %s
    Viewing Commentary = %s
    Sorting Resources By Topic = %s
    """ % (firstname, lastname, email, feedback, rating, vastResourceCollection, addingResources, viewingCommentary, sortingResroucesByTopic)

    return msg

## end createEmail():


################################################################################
def submitFeedback():
    """
    Presentation layer that shows Thank You page after feedback is submitted.
    Feedback is sent to the webmaster.
    """

    print("""
    <h2>Thanks For The Feedback!</h2>
    <p>Your Feedback Was Sent To Us For Review</p>
    <p>Enjoy This Video Before Browsing More Resources!</p>
    <iframe width="560" height="315" src="//www.youtube.com/embed/9p0BqUcQ7i0?list=PLAEBF3913C725DC73" frameborder="0" allowfullscreen></iframe>
    <br><br>
    
    <form>
            <input type="submit" value="Return To Homepage">
    </form>
    """)
 
## end: def submitFeedback():


################################################################################
def sendEmail(sender, recipient, msg):
    """
    Connect up to the SMTP server and send the message 
    from the sender (site vistor) to the recipient (webmaster).
    """

    ## Create a mailer object 
    smtp = smtplib.SMTP()

    ## Connect to the outgoing mail server 
    smtp.connect("acs-smtp.bu.edu",25) 
    r = smtp.helo("bkvisler")

    ## Send the message
    r = smtp.sendmail(sender, recipient, msg)

    # goodbye
    smtp.quit()

## end: def sendEmail():


################################################################################
if __name__ == "__main__":

    ## Get form field data
    form = cgi.FieldStorage()

    ## Debugging information
    #print("DEBUG:", form, "<br>")
    
    doHTMLHead("Online Design Inspiration")


    ## SHOW ALL RESOURCES :: Obtain website data and then present the data
    if "showWebsiteData" in form:
        websiteData = getAllWebsites()
        showWebsiteData(websiteData)



    ## SHOW RESOURCES BY TOPIC :: Obtain website data given a choosen topic and
    ##  present the data
    elif "showWebsitesByTopic" in form and "topic" in form:
        topic = form["topic"].value
        websiteData = getAllWebsitesByTopic(topic)
        showWebsiteData(websiteData)



    ## SHOW ADD A RESOURCE FORM :: Show add new website/resource form
    elif "showAddAWebsiteForm" in form:
        showAddAWebsiteForm()



    ## ADD A RESOURCE :: Complete adding the website
    elif "addAWebsite" in form:

        # Ensure all form fields are filled out
        if "siteTitle" in form and "url" in form and "description" in form and "pictureURL" in form and "logoURL" in form:
            siteTitle = form["siteTitle"].value
            url = form["url"].value
            description = form["description"].value
            topic = form["topic"].value
            pictureURL = form["pictureURL"].value
            logoURL = form["logoURL"].value

            # Complete the Add Website
            rowcount = addAWebsite(siteTitle, url, description, topic, pictureURL, logoURL)

            # Notify user of (un)succesful attempt
            if rowcount == 1:
                print("""
                <p>Add Website Succeeded</p>
                <form>
                    <input type="submit" name="showWebsiteData" value="Show Updated Resource List">
                </form>
                """)
            else:
                print("""
                <p>Add Website Failed</p>
                <p>Ensure That You Filled Out The Entire Form</p>
                """)

        # If not all form fields are completed, request the vistor fills them out
        else:
            print("<p>Make sure all form fields are filled, thanks.</p>")

            # Reshow the Add A Website Form
            showAddAWebsiteForm()



    ## SHOW UPDATE A RESOURCE FORM :: Show update a resource form, prefilled
    elif "showUpdateWebsiteForm" in form and "siteID" in form:
        siteID = form["siteID"].value
        websiteData = getOneWebsite(siteID)
        updateWebsiteForm(websiteData)



    ## UPDATE A RESOURCE :: Complete update of the resource
    elif "updateWebsite" in form:

        # Ensure all form fields are filled out
        if "siteID" in form and "url" in form and "description" in form and "pictureURL" in form and "logoURL" in form:
            siteID = form["siteID"].value
            url = form["url"].value
            description = form["description"].value
            pictureURL = form["pictureURL"].value
            logoURL = form["logoURL"].value

            # Complete the update
            rowcount = updateWebsite(siteID, url, description, pictureURL, logoURL)

            # Notify user of (un)succesful attempt
            if rowcount == 1:
                print("""
                <p>Update Website Succeeded</p>
                <form>
                    <input type="submit" name="showWebsiteData" value="Show Updated Resource List">
                </form>
                """)
            else:
                print("""
                <p>Update Website Failed</p>
                <p>Ensure That You Filled Out All Form Fields Or Changed At Least One</p>
                """)

        # If not all form fields are completed, request the vistor fills them out
        else:
            print("<p>Make sure all form fields are filled, thanks.</p>")

            # Reshow the Update Website Form
            siteID = form["siteID"].value
            websiteData = getOneWebsite(siteID)
            updateWebsiteForm(websiteData)



    ## SHOW COMMENTARY AND WEBSITE DETAILS:: Show choosen website details and
    ##  respecitve comments along with add a comment form
    elif "showCommentary" in form and "siteID" in form:
        siteID = form["siteID"].value

        # Website information
        websiteData = getOneWebsite(siteID)
        showOneWebsite(websiteData)

        # Comments and new comment form
        comments = getComments(siteID)
        showComments(comments, siteID)



    ## ADD A COMMENT :: Complete adding a comment
    elif "addComment" in form:

        # Ensure all form fields are filled out
        if "siteID" in form and "fullname" in form and "comment" in form:
            siteID = form["siteID"].value
            fullname = form["fullname"].value
            comment = form["comment"].value

            # Complete the Add Comment
            rowcount = addComment(siteID, fullname, comment)

            ## Notify user of (un)succesful attempt, allow them to return to resource page
            if rowcount == 1:
                print("""
                <p>Add Comment Succeeded</p>
                <form>
                    <input type="hidden" name="siteID" value="%s">
                    <input type="submit" name="showCommentary" value="Return to Updated Commentary Page"></input>
                </form>
                """ % (siteID))
            else:
                print("""
                <p>Add Comment Failed</p>
                <p>Ensure That You Filled Out The Entire Form</p>
                """)
            
        # If not all form fields are completed, request the vistor fills them out.
        #   Then reshow the Website Information with Comment Form and Comments
        else:
            print("<p>Make sure all form fields are filled, thanks.</p>")
            siteID = form["siteID"].value
            websiteData = getOneWebsite(siteID)
            showOneWebsite(websiteData)
            comments = getComments(siteID)
            showComments(comments, siteID)



    ## SHOW FEEDBACK FORM :: Show feedback form
    elif "showFeedbackForm" in form:
        showFeedbackForm()



    ## SHOW FEEDBACK THANK YOU PAGE AND SEND EMAIL:: Show thank you page after
    ##  feedback is submitted and auto send the feedback to specified email below
    elif "submitFeedback" in form:

        # Ensure all form fields are filled out
        if "firstname" in form and "lastname" in form and "email" in form and "feedback" in form and "rating" in form:        
            firstname = form["firstname"].value
            lastname = form["lastname"].value
            email = form["email"].value
            feedback = form["feedback"].value
            rating = form["rating"].value

            # Get checkbox values (determine if checked or unchecked)
            if "vastResourceCollection" in form:
                 vastResourceCollection = "Checked"
            else:
                vastResourceCollection = "Unchecked"
                
            if "addingResources" in form:
                addingResources = "Checked"
            else:
                addingResources = "Unchecked"

            if "viewingCommentary" in form:
                viewingCommentary = "Checked"
            else:
                viewingCommentary = "Unchecked"

            if "sortingResroucesByTopic" in form:
                sortingResroucesByTopic = "Checked"
            else:
                sortingResroucesByTopic = "Unchecked"

            # Call the createEmail function
            msg = createEmail(firstname, lastname, email, feedback, rating, vastResourceCollection, addingResources, viewingCommentary, sortingResroucesByTopic)

            # Send the email and show the Thank You page
            sender = email
            recipient = "bkvisler@bu.edu" # Specify recipient (webmaster) email here
            sendEmail(sender, recipient, msg)
            submitFeedback()
            

        # If not all form fields are completed, request the vistor fills them out
        else:
            print("<p>Make sure all form fields are filled, thanks.</p>")
            showFeedbackForm()



    ## DEFAULT HOMEPAGE :: Show the Homepage and buttons to access other functions
    else:
        showHomepage()


    doHTMLTail()
