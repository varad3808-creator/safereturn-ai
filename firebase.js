// =========================================
// SAFERETURN FIREBASE CONFIG
// =========================================

import { initializeApp }

from "https://www.gstatic.com/firebasejs/12.13.0/firebase-app.js";

import {

getFirestore

}

from "https://www.gstatic.com/firebasejs/12.13.0/firebase-firestore.js";

import {

getAuth,
GoogleAuthProvider

}

from "https://www.gstatic.com/firebasejs/12.13.0/firebase-auth.js";

// =========================================
// FIREBASE CONFIG
// =========================================

const firebaseConfig = {

apiKey:
"AIzaSyBwZZ3Vyb-qSpA5u_w4u9CW7y2kbdiDR94",

authDomain:
"safereturn-f6632.firebaseapp.com",

projectId:
"safereturn-f6632",

storageBucket:
"safereturn-f6632.firebasestorage.app",

messagingSenderId:
"753626237442",

appId:
"1:753626237442:web:f197134274a596777cf51b",

measurementId:
"G-9GDWF67F4R"

};

// =========================================
// INITIALIZE FIREBASE
// =========================================

const app =
initializeApp(firebaseConfig);

// =========================================
// FIRESTORE DATABASE
// =========================================

const db =
getFirestore(app);

// =========================================
// FIREBASE AUTH
// =========================================

const auth =
getAuth(app);

// =========================================
// GOOGLE PROVIDER
// =========================================

const provider =
new GoogleAuthProvider();

provider.setCustomParameters({

prompt:"select_account"

});

// =========================================
// EXPORTS
// =========================================

export {

app,
db,
auth,
provider

};
