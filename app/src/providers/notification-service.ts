import { Injectable } from '@angular/core';

/**
 * NotificationService
 * Handle notification from the Push service
 * Patrick Champion - 14.12.2016
 */
@Injectable()
export class NotificationService {

  // notifications queue
  private queue: any[];

  // notification handler
  private handling: boolean;
  private handlers: any;
  private defaultHandler: any;

  /**
   * Constructor
   */
  constructor() {
    console.log('[NotificationService] initialize')

    // empty queue
    this.queue = [];

    // no handler
    this.handling = false;
    this.handlers = {};
    this.defaultHandler = (n) => console.log(JSON.stringify(n));
  }

  /**
   * Add a new notification
   * @param notification
   */
  notify(notification) {

    // add the notification and handle it
    this.queue.push(notification);
    if(!this.handling)
      this.handle();
  }

  /**
   * Add a new handler
   */
  addHandler(title, handler) {
    this.handlers[title] = handler;
  }

  /**
   * Set the default handler
   */
  setDefaultHandler(handler) {
    this.defaultHandler = handler;
  }

  /**
   * Handle the notification queue
   */
  private handle() {

    // start
    this.handling = true;

    // get the notification and the handler
    let notification = this.queue.shift();
    let handler = this.handlers[notification.title];
    if(handler == null)
      handler = this.defaultHandler;

    // handle it
    handler(notification);

    // look for other
    if(this.queue.length > 0)
      this.handle();

    // end
    this.handling = false;
  }
}
