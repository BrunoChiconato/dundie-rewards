# Future Plans

Some features are not ready yet but are planned for future releases. Here are some of the features that are planned for future releases:

- `transfer`: Command to transfer points between employees or departments.
- `history`: Command to show the history of points movements.

## Password Protection

All the commands will require a e-mail and password, and then will check on the `users` table to validate the authentication.

## Role Based Access Control

Users that have the role `admin` on the `users` table will be able to run the commands: `load` and `add`. For other users those commands will be disabled.

The `show` command will allow filtering by `dept` and `email` for admins, but for other users only his own information will be shown.

The `transfer` command will allow the user to send points from his own balance to any other and will be password protected.

The `history` command allows the user to see his own movements, admin users can pass `--email` to see the movements of any other user.