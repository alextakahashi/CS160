'use strict';

console.log('Loading function');

const doc = require('dynamodb-doc');

const dynamo = new doc.DynamoDB();


/**
 * Demonstrates a simple HTTP endpoint using API Gateway. You have full
 * access to the request and response payload, including headers and
 * status code.
 *
 * To scan a DynamoDB table, make a GET request with the TableName as a
 * query string parameter. To put, update, or delete an item, make a POST,
 * PUT, or DELETE request respectively, passing in the payload to the
 * DynamoDB API as a JSON body.
 */
exports.handler = (event, context, callback) => {
    //console.log('Received event:', JSON.stringify(event, null, 2));

    const done = (err, res) => callback(null, {
        statusCode: err ? '400' : '200',
        body: err ? err.message : JSON.stringify(res),
        headers: {
            'Access-Control-Allow-Headers': 'x-Requested-With',
            'Access-Control-Allow-Origin': '*',
            "Access-Control-Allow-Credentials" : true,
            'Content-Type': 'application/json',
        },
    });

    switch (event.httpMethod) {
        case 'GET':
            dynamo.scan({ TableName: event.queryStringParameters.TableName }, done);
            break;
        case 'POST':
            var json = JSON.parse(event.body);
            if (json["type"] == 'POST') {
                dynamo.putItem(json["data"], done);
            }
            else if (json["type"] == 'PUT') {
                dynamo.updateItem(json["data"], done);
            }
            else if (json["type"] == 'DELETE') {
                dynamo.deleteItem(json["data"], done);
            }
            else if (json["type"] == 'QUERY') {
                dynamo.scan(json["data"], done);
            } else{
                done(new Error(`Unsupported method "${json["type"]}"`))
            }
            break;
        default:
            done(new Error(`Unsupported method "${event.httpMethod}"`));
    }
};