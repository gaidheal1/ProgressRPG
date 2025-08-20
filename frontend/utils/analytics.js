// analytics.js
import ReactGA from "react-ga4";

export const GA_TRACKING_ID = "G-RZ2XJ07X68X"; // replace with your GA4 measurement ID

export const initGA = () => {
  ReactGA.initialize(GA_TRACKING_ID);
};

export const logPageView = (path) => {
  ReactGA.send({ hitType: "pageview", page: path });
};
