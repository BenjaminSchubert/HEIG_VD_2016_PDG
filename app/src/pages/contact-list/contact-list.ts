import "rxjs/add/operator/combineLatest";
import { BehaviorSubject } from "rxjs/BehaviorSubject";
import { Observable } from "rxjs/Observable";
import { Component } from "@angular/core";
import { NavController, App, AlertController, ActionSheetController } from "ionic-angular";
import { AddContact } from "../add-contact/add-contact";
import { CreateGathering } from "../create-gathering/create-gathering";
import { ContactsService } from "../../providers/contacts-service";
import { GatheringService } from "../../providers/gathering-service";
import { MeService } from "../../providers/me-service";
import { IUser } from "../../lib/stubs/user";


@Component({
    templateUrl: "contact-list.html",
})
export class ContactList {
    public filteredFriends$: Observable<IUser[]>;

    public blockedFriends$: Observable<IUser[]>;
    public friends$: Observable<IUser[]>;
    public friendRequestsReceived$: Observable<IUser[]>;
    public friendRequestsSent$: Observable<IUser[]>;

    public filter$: BehaviorSubject<string>;
    public checkedUsers: IUser[] = [];

    constructor(public navCtrl: NavController,
                public app: App,
                public service: ContactsService,
                public alertCtrl: AlertController,
                public actionSheetCtrl: ActionSheetController,
                public gatheringService: GatheringService,
                public meService: MeService) {

        this.filter$ = new BehaviorSubject("");

        this.filteredFriends$ = this.service.$.combineLatest(
            this.filter$,
            (users: IUser[], filter) => {
                filter = filter.trim().toLowerCase();
                if (filter === "") {
                    return users;
                }
                return users.filter((user: IUser) => user.friend.username.toLowerCase().match(filter));
            },
        );

        this.friendRequestsReceived$ = this.filteredFriends$.map((users: IUser[]) =>
            users.filter((user: IUser) => !user.initiator && !user.is_accepted && !user.is_hidden));

        this.friendRequestsSent$ = this.filteredFriends$.map((users: IUser[]) =>
            users.filter((user: IUser) => user.initiator && !user.is_accepted));

        this.friends$ = this.filteredFriends$.map((users: IUser[]) =>
            users.filter((user: IUser) => user.is_accepted && !user.is_blocked && !user.is_hidden));

        this.blockedFriends$ = this.filteredFriends$.map((users: IUser[]) =>
            users.filter((user: IUser) => user.is_blocked));
    }

    public ionViewWillEnter() {
        this.service.fetch().subscribe();
        this.meService.fetch().then();
    }

    public filterBy(event: any) {
        this.filter$.next(event.target.value);
    }

    public handleRequest(item) {
        this.alertCtrl.create({
            buttons: [
                {text: "Cancel"},
                {handler: () => this.service.hide(item.id).subscribe(), text: "Hide"},
                {handler: () => this.service.accept(item.id).subscribe(), text: "Accept"},
            ],
            enableBackdropDismiss: false,
            message: "Click OK to accept the friend request",
            title: "Accept " + item.friend.username + " ?",
        }).present().then();
    }

    public handleFriend(item) {
        this.actionSheetCtrl.create({
            buttons: [
                { handler: () => this.service.block(item.id).subscribe(), text: "Block" },
                {text: "Cancel", role: "cancel"},
            ],
            cssClass: "action-sheets-basic-page",
            title: item.friend.username,
        }).present().then();
    }

    public handleBlockedFriend(item) {
        this.alertCtrl.create({
            buttons: [
                {text: "Cancel"},
                { handler: () => this.service.unblock(item.id).subscribe(), text: "OK" },
            ],
            enableBackdropDismiss: false,
            message: "Click OK to unblock",
            title: "Unblock " + item.friend.username + " ?",
        }).present().then();
    }

    public addContact() {
        this.app.getRootNav().push(AddContact).then();
    }

    public createGathering() {
        // Reset gathering
        this.gatheringService.status = "create";
        this.gatheringService.initiator = true;
        this.gatheringService.meetings = {};
        this.gatheringService.meetings.organiser = this.meService.me;
        this.gatheringService.meetings.participants = this.checkedUsers.map((u: IUser) => {
            // FIXME : clean type
            return <any> {user: u.friend};
        });

        this.app.getRootNav().push(CreateGathering).then();
    }

    public check(event: any, user: IUser) {
        if (event.checked) {
            this.checkedUsers.push(user);
        } else {
            this.checkedUsers.splice(this.checkedUsers.findIndex((u: IUser) => u === user), 1);
        }
    }

}
