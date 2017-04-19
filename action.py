from __future__ import print_function
import boto.dynamodb

# Global access to connection. We'll need it across the board so initialize it now.
aws_access_key_id='AKIAJTXGYAYQRU4666WA'
AWSSecretKey='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'

conn = boto.dynamodb.connect_to_region(
        'us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=AWSSecretKey
        )


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
set_alarm_response = "What time would you like to wake up at? " + set_alarm_options
set_alarm_reprompt = set_alarm_options


session_end_response = "Quitting Session.  Your alarm has been set to " + alarm_set_time


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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    print('LAUNCH')
    session_attributes = create_dialog_attributes("")
    card_title = "Welcome"
    speech_output = welcome_response
    reprompt_text = welcome_reprompt
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_settings_response():
    print('Settings')
    session_attributes = create_dialog_attributes("")
    card_title = "Settings"
    speech_output = settings_response
    reprompt_text = settings_reprompt
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_set_alarm_response():
    print('Set Alarm')
    session_attributes = create_dialog_attributes("")
    card_title = "Set Alarm"
    speech_output = set_alarm_response
    reprompt_text = set_alarm_reprompt
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

def create_dialog_attributes(dialog_request, dialog=0, recipe=None):
    return {
        "dialogRequest": dialog_request,
        "dialog": dialog,
        "recipe": recipe
        }

def stop_handle(intent, session):
    session_attributes = {}
    reprompt_text = None
    card_title = "Stop"
    should_end_session = False
    speech_output = "Okay."

    if 'attributes' in session:
        session_attributes = session['attributes']
        if session_attributes['dialog'] > 0:
            speech_output += " Returning you to the main menu."
            session_attributes['dialog'] = 0
        else:
            handle_session_end_request()

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def dialog(intent, session):
    default_dialog = "What would you like to do?"
    failure_speech = "I couldn't make that configuration. Would you like to try again?"  
    session_attributes = {}
    reprompt_text = None
    card_title = intent['name']
    should_end_session = False

    if 'Item' in intent['slots']:
        dialog_request = intent['slots']['Item']['value']
        session_attributes = create_dialog_attributes(dialog_request)
        speech_output = default_dialog

        #At this point, you should get the table and then push stuff into it.
        table = conn.get_table('wakeMeUpInside')
        #item = table.scan().response

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
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

def howto(intent, session):
    session_attributes = {}
    reprompt_text = None
    card_title = intent['name']
    should_end_session = False
    card_title = "Help"
    speech_output = "You can say these things. \
            Find recipe. \
            I'd like to make recipe. Exit. Quit."

    if 'attributes' in session:
        session_attributes = session['attributes']

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    # print("on_session_started requestId=" + session_started_request['requestId']
    #       + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    # print("on_launch requestId=" + launch_request['requestId'] +
    #       ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    # print("on_intent requestId=" + intent_request['requestId'] +
    #       ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "SettingsIntent":
        return get_settings_response()
    elif intent_name == "SetAlarmIntent":
        return get_set_alarm_response()
    elif intent_name == "MyHelpIntent":
        return howto(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "MyStopIntent":
        return stop_handle(intent, session)
    elif intent_name == "MyRestartIntent":
        return restart_handle(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    # print("on_session_ended requestId=" + session_ended_request['requestId'] +
    #       ", sessionId=" + session['sessionId'])
    # add cleanup logic here
    #return stop_handle(session_ended_request, session)
    return build_response(create_dialog_attributes(""), build_speechlet_response(
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
