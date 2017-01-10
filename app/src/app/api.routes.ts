const BASE_URL = "https://rady.benschubert.me/api/";
const API_V1_URL = BASE_URL + "v1/";

const AUTH_URL = API_V1_URL + "auth/";
export const LOGIN_URL = AUTH_URL + "login/";
export const REFRESH_URL = AUTH_URL + "refresh/";
export const PASSWORD_RESET_URL = AUTH_URL + "password-reset/";

export const FCM_REGISTRATION_URL = API_V1_URL + "fcm/devices/";

export const USERS_URL = API_V1_URL + "users/";
export const ACCOUNT_URL = USERS_URL + "me/";
export const FRIENDS_URL = USERS_URL + "friends/";
export const ALL_FRIENDS_URL = FRIENDS_URL + "all/";
