// Import the functions you need from the SDKs you need
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { getAnalytics, isSupported } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyDUpClU3Im_4opujVanxvcCjhXARPnTYuM",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "liminal-c161f.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "liminal-c161f",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "liminal-c161f.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "193830945358",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:193830945358:web:4126932ba31399fcbcf91f",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-4KKZKLCF67",
};

export const isFirebaseConfigured = () => {
  return Boolean(
    firebaseConfig.apiKey &&
    firebaseConfig.apiKey.length > 10 &&
    !firebaseConfig.apiKey.includes("YOUR_API_KEY")
  );
};

let app = null;
let auth = null;
let googleProvider = null;
let analytics = null;

try {
  if (isFirebaseConfigured()) {
    app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();
    googleProvider.setCustomParameters({ prompt: "select_account" });

    if (typeof window !== "undefined") {
      isSupported()
        .then((supported) => {
          if (supported) {
            analytics = getAnalytics(app);
          }
        })
        .catch(() => {});
    }
  }
} catch (err) {
  console.warn("Firebase initialization deferred:", err.message);
}

export { app, auth, analytics, googleProvider };

export const signInWithGoogle = async () => {
  if (!isFirebaseConfigured() || !auth) {
    throw new Error(
      "Firebase credentials not yet provided. Please enter your Firebase API configuration."
    );
  }
  const result = await signInWithPopup(auth, googleProvider);
  return result.user;
};

export const logOutFirebase = async () => {
  if (auth) {
    await signOut(auth);
  }
};