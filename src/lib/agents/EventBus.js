/**
 * EventBus - The Backbone of FNX Talent Factory (Event-Driven)
 * This simple implementation uses EventEmitter to simulate a Message Queue for MVP.
 */
import { EventEmitter } from 'events';

class EventBus extends EventEmitter {
    constructor() {
        super();
        this.name = "FNX_EVENT_BUS";
    }

    /**
     * Publish an event to the bus
     * @param {string} eventName 
     * @param {Object} data 
     */
    publish(eventName, data) {
        console.log(`[${this.name}] >>> EMITTING: ${eventName}`);
        this.emit(eventName, data);
    }

    /**
     * Subscribe to an event
     * @param {string} eventName 
     * @param {Function} callback 
     */
    subscribe(eventName, callback) {
        console.log(`[${this.name}] <<< SUBSCRIBING TO: ${eventName}`);
        this.on(eventName, callback);
    }
}

export const eventBus = new EventBus();
