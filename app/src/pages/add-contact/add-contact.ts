import { BehaviorSubject } from "rxjs/BehaviorSubject";
import { Observable } from "rxjs/Observable";
import { Component } from "@angular/core";
import { Response } from "@angular/http";
import { AlertController } from "ionic-angular";
import { ContactsService } from "../../providers/contacts-service";
import { IUser } from "../../lib/stubs/user";


/**
 * This page allows to add contact from different sources
 *
 * @author Patrick Champion
 */
@Component({
    templateUrl: "add-contact.html",
})
export class AddContact {
    public noInputEntered: boolean = true;
    public users$: BehaviorSubject<IUser[]>;
    public addedUsers$: BehaviorSubject<IUser[]>;
    public displayedUsers$: Observable<IUser[]>;

    constructor(private service: ContactsService,
                private alertCtrl: AlertController) {
        this.users$ = new BehaviorSubject([]);
        this.addedUsers$ = new BehaviorSubject([]);
        this.displayedUsers$ = this.users$.combineLatest(
            this.addedUsers$,
            (all: IUser[], added: IUser[]) =>
                all.filter((u1: IUser) => added.find((u2: IUser) => u1.id === u2.id) === undefined),
        );
    }

    public ionViewWillEnter() {
        this.users$.next([]);
        this.addedUsers$.next([]);
    }

    public search(event) {
        this.noInputEntered = false;
        let s = event.target.value.trim();
        if (s.length === 0) {
            this.users$.next([]);
            return;
        }

        this.service.search(s).debounceTime(500).subscribe((res: Response) => {
            this.users$.next(res.json());
            this.addedUsers$.next([]);
        });
    }

    public addContact(user: IUser) {
        // Ask the user for confirmation before the adding
        this.alertCtrl.create({
            buttons: [
                {text: "Cancel"},
                {
                    handler: () => this.service.addFriend(user).subscribe(() =>
                        this.addedUsers$.next(this.addedUsers$.value.concat(user))),
                    text: "Yes",
                },
            ],
            enableBackdropDismiss: false,
            message: `Send a friend request to ${(<any> user).username} ?`,
            title: "Confirmation",
        }).present().then();
    }
}
