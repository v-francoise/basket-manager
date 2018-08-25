// See https://github.com/dialogflow/dialogflow-fulfillment-nodejs
// for Dialogflow fulfillment library docs, samples, and to report issues
'use strict';

const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const http = require('http');

const apiHost = null; // https://my-publicly-accessible-endpoint;
const apiPort = null; // 443;

process.env.DEBUG = 'dialogflow:*'; // enables lib debugging statements

exports.dialogflowFirebaseFulfillment = functions.https.onRequest((request, response) => {
  const agent = new WebhookClient({ request, response });
  console.log('Dialogflow Request headers: ' + JSON.stringify(request.headers));
  console.log('Dialogflow Request body: ' + JSON.stringify(request.body));

  function httpRequest(params, postData) {
    return new Promise(function(resolve, reject) {
      var req = http.request(params, function(res) {
        if (res.statusCode < 200 || res.statusCode >= 300) {
          return reject(new Error('statusCode=' + res.statusCode));
        }
        var body = [];
        res.on('data', function(chunk) {
          body.push(chunk);
        });
        // resolve on end
        res.on('end', function() {
        try {
          body = JSON.parse(Buffer.concat(body).toString());
        } catch(e) {
          reject(e);
        }
          resolve(body);
        });
      });
      req.on('error', function(err) {
        reject(err);
      });
      if (postData) {
        req.write(postData);
      }
      req.end();
    });
  }

  function createBasket(agent) {
    let options = {
      port: apiPort,
      hostname: apiHost,
      method: 'POST',
      headers: {'content-type': 'application/json'},
      path: '/baskets'
    };

    let mobile = agent.parameters.mobile;
    let sim = agent.parameters.sim;
    let broadband = agent.parameters.broadband;

    return httpRequest(options)
    .then((basket) => {
      console.log(basket);
      agent.setContext({
        name: 'basket-context',
        parameters: {
          basketId: basket["id"],
          mobile: mobile,
          sim: sim,
          broadband: broadband
        },
      });
      agent.add("Okay. What do you wish to buy?");
    })
    .catch(err => {
      console.log(err);
      agent.add("An error has occurred.");
    });
  }

  function getBasket(agent) {
    let basketId = agent.getContext("basket-context").parameters.basketId;

    let options = {
      port: apiPort,
      hostname: apiHost,
      method: 'GET',
      path: '/baskets/' + basketId
    };

    return httpRequest(options).then((basket) => {
      agent.add("Your basket contains:" + basket.products);
    });
  }

  function addProduct(agent, productName, productType) {
    let basketContext = agent.getContext("basket-context");
    let basketId = basketContext.parameters.basketId;

    let options = {
      port: apiPort,
      hostname: apiHost,
      method: 'POST',
      headers: {'content-type': 'application/json'},
      path: '/baskets/' + basketId + '/add',
    };

    let payload = {
      name: productName,
      type: productType,
      basket_id: basketId
    };

    return httpRequest(options, payload)
    .then((basket) => {
      console.log(basket);
      agent.add(`${productName} has been added to your basket. Anything else?`);
      let newBasketContext = {
        name: basketContext.name,
        parameters: basket.parameters
      }
      newBasketContext.parameters[productType] = productName;
      agent.setContext(newBasketContext);
    })
    .catch((error) => {
      console.log(error);
      agent.add(
        `${productName} could not be added your basket.
         Only a single ${productType} can be added in your basket.`);
    });
  }

  function addSim(agent) {
    let product = agent.parameters.sim;
    addProduct(agent, product, 'sim');
  }

  function addBroadband(agent) {
    let product = agent.parameters.broadband;
    addProduct(agent, product, 'broadband');
  }

  function addMobile(agent) {
    let product = agent.parameters.mobile;
    addProduct(agent, product, 'mobile');
  }

  function pay(agent) {
    let basketId = agent.getContext("basket-context").parameters.basketId;

    let options = {
      port: apiPort,
      hostname: apiHost,
      method: 'GET',
      path: '/baskets/' + basketId
    };

    return httpRequest(options)
    .then((basket) => {
      agent.add("Done! You bought:" + basket.products);
    })
    .catch(err => {
      console.log(err);
      agent.add("An error has occurred.");
    });
  }

  function fallback(agent) {
    agent.add(`I didn't understand`);
    agent.add(`I'm sorry, can you try again?`);
  }

  // Run the proper function handler based on the matched Dialogflow intent name
  let intentMap = new Map();
  intentMap.set('Default Fallback Intent', fallback);

  intentMap.set('start basket', createBasket);
  intentMap.set('get basket', getBasket);
  intentMap.set('add sim', addSim);
  intentMap.set('add mobile', addMobile);
  intentMap.set('add broadband', addBroadband);
  intentMap.set('pay', pay);

  agent.handleRequest(intentMap);
});
