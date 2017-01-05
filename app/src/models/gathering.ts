import { RadyUser } from './user';

/**
 * RadyGathering
 * Model for meetings
 * Patrick Champion - 05.01.2017
 */
export class RadyGathering {

    constructor(
        public initiator: RadyUser,
        public participants: RadyUser[],
        public mode: string = null
    ) {}
}