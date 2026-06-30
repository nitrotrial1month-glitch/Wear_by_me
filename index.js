const express = require('express');
const admin = require('firebase-admin');
const cors = require('cors');

// 🔴 আপনার ফায়ারবেস অ্যাডমিন কি (Key) ফাইলটি এখানে লিংক করা হলো
const serviceAccount = require('./firebase-service-account.json');

// ফায়ারবেস ইনিশিয়ালাইজ (চালু) করা
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const app = express();

// মিডলওয়্যার (যাতে ফ্লাটার অ্যাপ থেকে ডেটা রিসিভ করতে পারে)
app.use(cors());
app.use(express.json());

// 🔴 নোটিফিকেশন পাঠানোর API (মেইন ইঞ্জিন)
app.post('/api/send-notification', async (req, res) => {
  // ফ্লাটার অ্যাপ থেকে টোকেন, টাইটেল এবং বডি আসবে
  const { token, title, body } = req.body;

  // কোনো ডেটা মিসিং থাকলে এরর দেখাবে
  if (!token || !title || !body) {
    return res.status(400).json({ error: "Token, title, and body are required!" });
  }

  // ফায়ারবেসের জন্য মেসেজ সাজানো
  const payload = {
    notification: {
      title: title,
      body: body
    },
    token: token // ইউজারের ফোনের ইউনিক আইডি
  };

  try {
    // ফায়ারবেসকে মেসেজ পাঠাতে বলা
    const response = await admin.messaging().send(payload);
    console.log('✅ Successfully sent message:', response);
    res.status(200).json({ success: true, message: "Notification sent successfully!", response });
  } catch (error) {
    console.log('❌ Error sending message:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// বেসিক হোম রাউট (সার্ভার চেক করার জন্য)
app.get('/', (req, res) => {
  res.send('Wear By Me Backend is Running! 🚀');
});

// সার্ভার চালু করা
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server is running on port ${PORT}`);
});

