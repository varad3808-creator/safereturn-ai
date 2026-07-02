const { onRequest } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const cors = require("cors")({ origin: true });
const { Resend } = require("resend");

const RESEND_API_KEY = defineSecret("RESEND_API_KEY");

exports.contact = onRequest(
  {
    secrets: [RESEND_API_KEY],
  },
  async (req, res) => {
    cors(req, res, async () => {
      if (req.method !== "POST") {
        return res.status(405).json({
          success: false,
          message: "Method not allowed",
        });
      }

      try {
        const resend = new Resend(RESEND_API_KEY.value());

        const {
          name,
          email,
          subject,
          message,
        } = req.body;

        if (
          !name ||
          !email ||
          !subject ||
          !message
        ) {
          return res.status(400).json({
            success: false,
            message: "Please fill all fields.",
          });
        }

        await resend.emails.send({

          from: "onboarding@resend.dev",

          to: "safe.return3808@gmail.com",

          replyTo: email,

          subject: `SafeReturn Contact Form - ${subject}`,

          html: `
            <h2>New Contact Form Submission</h2>

            <hr>

            <p><strong>Name:</strong> ${name}</p>

            <p><strong>Email:</strong> ${email}</p>

            <p><strong>Subject:</strong> ${subject}</p>

            <hr>

            <p>${message}</p>

            <br>

            <small>
            Sent from SafeReturn Contact Form
            </small>
          `,
        });

        return res.status(200).json({
          success: true,
          message: "Email sent successfully.",
        });

      } catch (error) {

        console.error(error);

        return res.status(500).json({

          success: false,

          message: error.message,

        });

      }
    });
  }
);