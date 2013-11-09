<?php

    
/**
 * @file
 * This is the Form API Tutorial from the handbook.
 *
 * It goes through 10 form examples of increasing complexity to demonstrate
 * Drupal 7 Form API.
 *
 * Links are provided inline for the related handbook pages.
 *
 * @see http://drupal.org/node/262422
 */

 
 /**
  * Create the form.
  */
function queue_helper_add_to_queue($form, &$form_state) {
  $form['description'] = array(
    '#type' => 'item',
    '#title' => t('A form to add item to SQS'),
  );

  $form['qname'] = array(
    '#type' => 'textfield',
    '#title' => t('Queue name'),
    '#maxlength' => 1024
  );
  
  
  $form['item'] = array(
    '#type' => 'textfield',
    '#title' => t('Item'),
    '#maxlength' => 1024
  );

  // Adds a simple submit button that refreshes the form and clears its
  // contents. This is the default behavior for forms.
  $form['submit'] = array(
    '#type' => 'submit',
    '#value' => 'Submit',
  );
  return $form;
}



/**
 * Validation - make sure it is not empty().
 */
function queue_helper_add_to_queue_validate($form, &$form_state) {
        
    $item = $form_state['values']['qname'];
    if (!$item) {
        form_set_error('item', 'Please enter the name to submit too.');
    }
    
    $item = $form_state['values']['item'];
    if (!$item) {
        form_set_error('item', 'Please enter an item to submit.');
    }
}

/**
 * Submit function.
 *
 * Adds the Item to the SQS Queue. AWS settings are retreived via the awssdk module, which also provides the sdk.
 */
function queue_helper_add_to_queue_submit($form, &$form_state) {
  
    libraries_load('awssdk');
    global $conf;
 
    $qname = $form_state['values']['qname'];
    $item = $form_state['values']['item'];

    $client = new AmazonSQS(array(
    'key'    => $conf['aws_key'],
    'secret' => $conf['aws_secret'],
    ));
    
    watchdog("queue helper", "Messsage sent to SQS:" . $item);
    
    $response = $client->create_queue($qname);
    $queue_url = (string) $response->body->CreateQueueResult->QueueUrl;

    $client->send_message( $queue_url, $item);
    
    drupal_set_message(t('The form has been submitted.'));
  
}

