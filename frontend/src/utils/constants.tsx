/**
 * const domain = 'https://catholicviet.jp:8000';*/
 const domain = 'http://localhost:8000'

const apiURL = '/api';
const authURL = '/rest-auth';

export const VCJTOKEN = 'vcj_token';
export const EXPIRATION_DATE = 'vcjexpDate';

export const endpoint = `${domain}${apiURL}`;
export const authEndPoint = `${domain}${authURL}`

export const loginEndPoint = `${authEndPoint}/login/`
export const signUpEndPoint = `${authEndPoint}/registration/`

export const newfeedsListURL = `${endpoint}/products/`;
export const newfeedDetailURL = (id: number) => `${endpoint}/products/${id}/`;
export const updateNewFeedURL = (id: number, update_type: string) =>
  `${endpoint}/newfeed/${id}/update/?type=${update_type}`;
export const myregisterURL = (churchId: number) =>
  `${endpoint}/massregister/?churchId=${churchId}`;
export const massregisterCreateURL = `${endpoint}/massregister/create/`;
export const registerUpdateURL = (id: number) =>
  `${endpoint}/massregister/${id}/update/`;