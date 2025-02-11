// Required libraries
const dotenv = require('dotenv');
const fetch = require('node-fetch');
const nodemailer = require('nodemailer');
const { DAVClient } = require('node-caldav');

// Load environment variables from .env file
dotenv.config();

const APPLE_ID = process.env.APPLE_ID;
const APPLE_SPECIFIC_PASSWORD = process.env.APPLE_APP_PW;
const NAME = process.env.NAME;
const CARRIER = process.env.CARRIER;
const PHONE_NUMBER = process.env.NUMBER;
const FAKE_EMAIL = process.env.FAKE_EMAIL;
const FAKE_PASSWORD = process.env.FAKE_PW;
const APP_PASSWORD = process.env.APP_PW;

// Convert time to 12-hour format
function convertTime(time) {
    const date = new Date(time);
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const adjustedHours = hours % 12 || 12;
    return `${adjustedHours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
}

// Get daily events from Apple calendars
async function getDayEvents(calendars) {
    const today = new Date();
    const todayStart = new Date(today.setHours(0, 0, 0, 0)); // Midnight
    const todayEnd = new Date(today.setHours(23, 59, 59, 999)); // 11:59 PM

    const dailyEvents = [];

    for (const calendar of calendars) {
        const events = await calendar.dateSearch(todayStart, todayEnd);
        for (const event of events) {
            dailyEvents.push({
                summary: event.summary,
                start_time: event.start,
                end_time: event.end,
                location: event.location || 'No location',
            });
        }
    }

    return dailyEvents;
}

// Create a message from daily events
function getMessage(dailyEvents) {
    if (dailyEvents.length === 0) {
        console.log("No events today.");
        return "No events today.";
    }

    let message = "Today's Events:\n";
    console.log("Today's Events:");

    dailyEvents.forEach(event => {
        const start = convertTime(event.start_time);
        const end = convertTime(event.end_time);
        message += `- ${event.summary} from ${start} to ${end} (Location: ${event.location})\n`;
        console.log(`- ${event.summary} from ${start} to ${end} (Location: ${event.location})`);
    });

    return message;
}

// Get events from calendar
async function getCalendarEvents() {
    const client = new DAVClient({
        server: "https://caldav.icloud.com/",
        credentials: {
            username: APPLE_ID,
            password: APPLE_SPECIFIC_PASSWORD,
        },
    });

    const principal = await client.principal();
    const calendars = await principal.calendars();
    const dailyEvents = await getDayEvents(calendars);
    return getMessage(dailyEvents);
}

// Send message using nodemailer
async function sendMessage(message) {
    const receiver = PHONE_NUMBER + CARRIER;

    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
            user: FAKE_EMAIL,
            pass: APP_PASSWORD,
        },
    });

    const mailOptions = {
        from: FAKE_EMAIL,
        to: receiver,
        subject: 'Daily Calendar Events',
        text: message,
    };

    try {
        await transporter.sendMail(mailOptions);
        console.log("Message sent:", message);
    } catch (error) {
        console.error("Error sending message:", error);
    }
}

// Main function
(async function main() {
    try {
        const message = await getCalendarEvents();
        await sendMessage(message);
    } catch (error) {
        console.error("Error:", error);
    }
})();
