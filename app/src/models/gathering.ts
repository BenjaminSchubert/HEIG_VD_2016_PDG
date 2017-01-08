import { RadyUser } from './user';

/**
 * RadyGathering
 * Model for meetings
 * Patrick Champion - 05.01.2017
 */
export class RadyGathering {

    public mode: string = null;
    public destination: any = null;

    constructor(
        public initiator: RadyUser,
        public participants: RadyUser[]
    ) {}
}