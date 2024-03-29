from __future__ import print_function

import pymysql
import random
import urllib, json



# Global access to connection. We'll need it across the board so initialize it now.
aws_access_key_id='AKIAJTXGYAYQRU4666WA'
AWSSecretKey='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'

conn = pymysql.connect(host='colinschoen.me',
                       user='wakemeup',
                       password='2GqydTHnQqaFfUxy',
                       db='wakemeup',
                       cursorclass=pymysql.cursors.DictCursor)


# Speech Outputs:
alarm_set_time = "9:30 AM "
settings_options = "You can say \
                    Set alarm \
                    or \
                    Change how I wake up "
welcome_response = "Hello, you have an alarm set for "+ alarm_set_time
welcome_reprompt = "Would you like to change your alarm? " + settings_options

settings_response = "Your alarm is currently set to " + alarm_set_time + ". "+ settings_options
settings_reprompt = settings_options

set_alarm_options = "You can say \
                     something like ... \
                     9:30AM." 
set_alarm_response = "What time would you like to wake up? " + set_alarm_options
set_alarm_reprompt = set_alarm_options

change_how_i_wake_up_options = "You can say \
                                math, \
                                trivia, \
                                weather, \
                                or \
                                quotes."
change_how_i_wake_up_response = "Choose how you would like to wake up. " + change_how_i_wake_up_options
change_how_i_wake_up_reprompt = change_how_i_wake_up_options

alarm_set_response = "Your alarm has been set to " + alarm_set_time

session_end_response = "Quitting Session.  Your alarm has been set to " + alarm_set_time

quote_me_weclome_response = "Good Morning! I will list you 2 quotes to get you started with your day. "
quote_me_end_response = "Thanks for listening.  Have a nice day!"


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def get_dialog_attributes(session):
    uid = session['user']['userId']
    preferences = get_preferences(uid)
    session_attributes = create_dialog_attributes()
    if 'attributes' in session:
        session_attributes = session['attributes']
    return session_attributes

def get_preferences(uid):
    preferences = {}
    result = select_query("SELECT value FROM settings WHERE uid=%s AND name=%s", (uid, "time"))
    if result:
        preferences["time"] = result["time"]
    else:
        preferences["time"] = "09:00"
    result = select_query("SELECT value FROM settings WHERE uid=%s AND name=%s", (uid, "method"))

    if result:
        preferences["method"] = result["method"]
    else:
        preferences["method"] = "trivia"
    return preferences

# --------------- Functions that control the skill's behavior ------------------






def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    print('LAUNCH')
    session_attributes = create_dialog_attributes()
    card_title = "Welcome"
    speech_output = welcome_response
    reprompt_text = welcome_reprompt
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_settings_response():
    print('Settings')
    session_attributes = create_dialog_attributes()
    card_title = "Settings"
    speech_output = settings_response
    reprompt_text = settings_reprompt
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_set_alarm_response():
    print('Set Alarm')
    session_attributes = create_dialog_attributes()
    card_title = "Set Alarm"
    speech_output = set_alarm_response
    reprompt_text = set_alarm_reprompt
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_change_how_i_wake_up_response():
    print("Change How I Wake Up")
    session_attributes = create_dialog_attributes()
    card_title = "Change How I Wake Up"
    speech_output = change_how_i_wake_up_response
    reprompt_text = change_how_i_wake_up_reprompt
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_help_response():
    session_attributes = {}
    card_title = "Help"
    speech_output = settings_options
    reprompt_text = settings_options
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = session_end_response
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def create_dialog_attributes(alarmTime="9:30 AM", method="math"):
    return {
        "alarm_time": alarmTime,
        "method": method,
        }

def invoke_alarm(intent, session):
    # Fetch the wake up type from the session
    attributes = session['attributes']
    method = attributes['method']
    assert method in methods, "Invalid method sent {}".format(method)
    
    # Use our dispatch dictionary
    return methods[method](intent, session)

    # We can add any hooks below here in the future

def insert_query(sql, values=()):
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
    conn.commit()

def select_query(sql, values=()):
    with conn.cursor() as cursor:
        cursor.execute(sql, values)
        result = cursor.fetchone()
    conn.commit()
    return result

def dialog(intent, session):
    default_dialog = "So you want to change your alarm time."
    failure_speech = "This did not work."  
    session_attributes = {}
    reprompt_text = None
    card_title = intent['name']
    should_end_session = False
    intent_name = intent['name']
    uid = session['user']['userId']

    if 'Time' in intent['slots']:
        time = intent['slots']['Time']['value']
        session_attributes = create_dialog_attributes(time)
        speech_output = "I have set your alarm for " + time
        result = select_query("SELECT * FROM settings WHERE uid=%s AND name=%s", 
                (uid, "time"))
        if not result:
            insert_query("INSERT INTO settings (uid, name, value) VALUES (%s, %s, %s)", (uid, "time", time))
        else:
            insert_query("UPDATE settings SET value=%s WHERE uid=%s AND name=%s", 
                    (time, uid, "time"))

    if 'Method' in intent['slots']:
        method = intent['slots']['Method']['value']
        # Must get time first
        session_attributes = create_dialog_attributes(method)
        speech_output = "You are now set up to wake up to " + method
        result = select_query("SELECT * FROM settings WHERE uid=%s AND name=%s", 
                (uid, "method"))
        if not result:
            insert_query("INSERT INTO settings (uid, name, value) VALUES (%s, %s, %s)", (uid, "method", method))
        else:
            insert_query("UPDATE settings SET value=%s WHERE uid=%s AND name=%s", 
                    (method, uid, "method"))

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def wakemeup(intent, session):
    default_dialog = "What would you like to do?"
    failure_speech = "I couldn't make that configuration. Would you like to try again?"  
    session_attributes = {}
    reprompt_text = None
    card_title = intent['name']
    should_end_session = False

    #This grabs every item. Consider using table.query() for this part.
    table = conn.get_table('wakeMeUpInside')
    item = table.scan().response

def mathme(intent, session):
    session_attributes = session['attributes']
    speech_output = ""
    reprompt_text = ""
    reprompt_text = ""
    card_title = intent['name']
    should_end_session = False
    was_question_correct = False
    questions_asked = 0
    intent_name = intent['name']
    if 'questions_asked' in session_attributes:
        questions_asked = session_attributes['questions_asked']

    #First, determine if a previous question was released. If so, check the response.
    if questions_asked > 0 and 'solution' in session_attributes:
        if intent_name == "MathNumberIntent":
            #Grab the solution and check it. If this fails for whatever reason, 
            #there's no error checking yet. But something was said out of order, 
            #probably.
            # try:
            potential_solution = intent['slots']['Number']['value']
            solution = session_attributes['solution']

            if int(potential_solution) == int(solution):
                speech_output += "Good job, that's correct!"
                was_question_correct = True
            else:
                speech_output += "That's not quite correct, please try again!"
                speech_output += "What is %d times %d?" % (session_attributes['num1'], session_attributes['num2'])
            # except:
            #     print("Error in asking questions for math me!")

    #Then, check if we've asked enough questions. If so, exit MathMe.
    if questions_asked > 2:
        should_end_session = True
        speech_output += "That's it, no more questions! Good morning!"

    #Finally, if we want to ask another question, do it.
    elif was_question_correct == True or (questions_asked < 1 and intent_name == "MathMeIntent"):
        num1 = random.randint(4,12)
        num2 = random.randint(4,12)
        solution = num1 * num2
        session_attributes['solution'] = solution
        session_attributes['num1'] = num1
        session_attributes['num2'] = num2
        speech_output += "What is %d times %d?" % (num1, num2)

        session_attributes['questions_asked'] = questions_asked + 1

    reprompt_text = speech_output
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def quoteme(intent, session):

    session_attributes = session['attributes']
    speech_output = quote_me_weclome_response
    reprompt_text = ""
    card_title = intent['name']
    should_end_session = True

    quote_count = 1

    while (quote_count < 3):
        url = "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1&callback="
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        quote = data[0]['content']
        speech_output = speech_output + quote_prologue + quote
        quote_count += 1

    speech_output += quote_me_end_response


    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def weatherme(intent, session):
    session_attributes = session['attributes']
    speech_output = "Good morning! "
    reprompt_text = ""
    card_title = intent['name']
    should_end_session = True
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo.places(1)%20where%20text%3D%22berkeley%2C%20ca%22)&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    right_now = data['query']['results']['channel']['item']['condition']
    speech_output += "Currently the weather is %s with a temperature of %s. " % (right_now['text'], right_now['temp'])
    today = data['query']['results']['channel']['item']['forecast'][0]
    speech_output += "Today, %s, it is %s with a high of %s and a low of %s." % (today['date'], today['text'], today['high'], today['low'])
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
 # Dispatch Dictionary
methods = {
        "math": mathme,
}

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SettingsIntent":
        return get_settings_response()
    elif intent_name == "InvokeAlarm":
        return invoke_alarm(intent, session)
    elif intent_name == "SetAlarmIntent":
        return get_set_alarm_response()
    elif intent_name == "SetAlarmAt":
        return dialog(intent, session)
    elif intent_name == "ChangeHowIWakeUp":
        return get_change_how_i_wake_up_response()
    elif intent_name == "MathMeIntent" or intent_name == "MathNumberIntent":
        return mathme(intent, session)
    elif intent_name == "QuoteMeIntent":
        return quoteme(intent, session)
    elif intent_name == "WeatherMeIntent":
        return weatherme(intent, session)
    elif intent_name == "MethodIntent":
        return dialog(intent, session)
    elif intent_name == "MyHelpIntent":
        return howto(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    return build_response(create_dialog_attributes(), build_speechlet_response(
        "", "", None, False))


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    # print("event.session.application.applicationId=" +
    #       event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
