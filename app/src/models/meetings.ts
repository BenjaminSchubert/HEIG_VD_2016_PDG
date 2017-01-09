import { RadyUser } from './user';

/**
 * RadyMeetings
 * Model for meetings
 * Patrick Champion - 08.01.2017
 */
export class RadyMeetings {

    id?: number;
    organiser?: RadyUser;
    place?: { 
        id?: number;
        latitude?: number;
        longitude?: number;
        name?: string;
    };
    participants?: {
        accepted?: boolean;
        arrived?: boolean;
        user?: RadyUser;
    }[];
    meetings_time?: string;
    type?: string;
    status?: string;
    on?: number;
}