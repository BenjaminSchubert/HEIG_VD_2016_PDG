# Messages PUSH

## Demandes d'ami

### Nouvelle demande
- **title** : New friend request
- **body** : {} wants to be your friend
- **data** : { type: "friend-request", friendship: id },
- **deferred** : oui

### Demande acceptée
- **title** : Friend request accepted
- **body** : {} is now your friend
- **data** : { type: "friend-request-accepted", meeting: id },
- **deferred** : oui

## Rencontres (messages par personne)

### Nouvelle demande de rencontre
- **title** : New meeting
- **body** : {} added you to a meeting
- **data** : { type: "new-meeting", meeting: id },
- **deferred** : oui

*Message annulé à la fin du meeting, si il n'a pas été transmis*

### Un utilisateur a accepté une rencontre
- **title** : Meeting update
- **body** : {} accepted the meeting
- **data** : { type: "user-accepted-meeting", meeting: id, participant: id },
- **deferred** : non

### Un utilisateur a refusé une rencontre
- **title** : Meeting update
- **body** : {} refused the meeting
- **data** : { type: "user-refused-meeting", meeting: id, participant: id },
- **deferred** : non

### Un utilisateur est arrivé au point de rencontre
- **title** : Meeting update
- **body** : {} has arrived to the meeting
- **data** : { type: "user-arrived-to-meeting", meeting: id, participant: id },
- **deferred** : non

## Rencontres (messages groupés)

### La rencontre a commencé
- **title** : Meeting in progress
- **body** : Go to the meeting now
- **data** : { type: "meeting-in-progress", meeting: id },
- **deferred** : non

### La rencontre est finie
- **title** : Meeting finished
- **body** : The meeting is now finished
- **data** : { type: "finished-meeting", meeting: id },
- **deferred** : non

### La rencontre est annulée
- **title** : Meeting canceled
- **body** : The meeting has been canceled
- **data** : { type: "canceled-meeting", meeting: id },
- **deferred** : non
