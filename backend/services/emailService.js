// backend/services/emailService.js
import nodemailer from "nodemailer";

// Create reusable transporter
const createTransporter = () => {
  // For development, you can use a service like Gmail or Mailtrap
  // For production, use a proper email service like SendGrid, AWS SES, etc.
  
  if (process.env.EMAIL_SERVICE === "gmail") {
    // Gmail configuration
    return nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASSWORD, // Use App Password for Gmail
      },
    });
  } else if (process.env.EMAIL_SERVICE === "smtp") {
    // Generic SMTP configuration
    return nodemailer.createTransport({
      host: process.env.SMTP_HOST,
      port: process.env.SMTP_PORT || 587,
      secure: process.env.SMTP_SECURE === "true", // true for 465, false for other ports
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASSWORD,
      },
    });
  } else {
    // Development mode - Use ethereal email (fake SMTP)
    console.warn("⚠️ No email service configured. Using Ethereal for testing.");
    // Note: For Ethereal, you need to create test account first
    // This is handled in the sendPasswordResetEmail function
    return null;
  }
};

// Send password reset email
export const sendPasswordResetEmail = async (email, resetToken, businessName) => {
  try {
    let transporter = createTransporter();

    // If no transporter (dev mode), create ethereal test account
    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransport({
        host: "smtp.ethereal.email",
        port: 587,
        secure: false,
        auth: {
          user: testAccount.user,
          pass: testAccount.pass,
        },
      });
      console.log("📧 Using Ethereal test email account:", testAccount.user);
    }

    const resetUrl = `${process.env.FRONTEND_URL || "http://localhost:3000"}/reset-password/${resetToken}`;

    const mailOptions = {
      from: `"TANAW Support" <${process.env.EMAIL_FROM || "noreply@tanaw.com"}>`,
      to: email,
      subject: "Password Reset Request - TANAW",
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .button { display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
            .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #666; }
            .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🔐 Password Reset Request</h1>
            </div>
            <div class="content">
              <p>Hi <strong>${businessName}</strong>,</p>
              
              <p>We received a request to reset your password for your TANAW account. Click the button below to create a new password:</p>
              
              <div style="text-align: center;">
                <a href="${resetUrl}" class="button">Reset My Password</a>
              </div>
              
              <p>Or copy and paste this link into your browser:</p>
              <p style="word-break: break-all; color: #667eea;">${resetUrl}</p>
              
              <div class="warning">
                <strong>⚠️ Security Notice:</strong>
                <ul style="margin: 10px 0;">
                  <li>This link will expire in <strong>1 hour</strong></li>
                  <li>If you didn't request this reset, please ignore this email</li>
                  <li>Your password will remain unchanged</li>
                </ul>
              </div>
              
              <p>Need help? Contact our support team.</p>
              
              <p>Best regards,<br>
              <strong>TANAW Team</strong></p>
            </div>
            <div class="footer">
              <p>This is an automated message from TANAW. Please do not reply to this email.</p>
              <p>&copy; ${new Date().getFullYear()} TANAW. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Hi ${businessName},

        We received a request to reset your password for your TANAW account.
        
        Click this link to reset your password: ${resetUrl}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email. Your password will remain unchanged.
        
        Best regards,
        TANAW Team
      `,
    };

    const info = await transporter.sendMail(mailOptions);

    if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVICE) {
      console.log("📧 Preview URL:", nodemailer.getTestMessageUrl(info));
    }

    console.log("✅ Password reset email sent to:", email);
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error("❌ Error sending password reset email:", error);
    throw new Error("Failed to send password reset email");
  }
};

// Send password reset confirmation email
export const sendPasswordResetConfirmationEmail = async (email, businessName) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransport({
        host: "smtp.ethereal.email",
        port: 587,
        secure: false,
        auth: {
          user: testAccount.user,
          pass: testAccount.pass,
        },
      });
    }

    const mailOptions = {
      from: `"TANAW Support" <${process.env.EMAIL_FROM || "noreply@tanaw.com"}>`,
      to: email,
      subject: "Password Successfully Changed - TANAW",
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .success { background: #d4edda; border-left: 4px solid #28a745; padding: 12px; margin: 20px 0; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>✅ Password Changed Successfully</h1>
            </div>
            <div class="content">
              <p>Hi <strong>${businessName}</strong>,</p>
              
              <div class="success">
                <strong>Your password has been successfully changed!</strong>
              </div>
              
              <p>This is a confirmation that your TANAW account password was recently changed.</p>
              
              <p>If you did not make this change, please contact our support team immediately.</p>
              
              <p>Best regards,<br>
              <strong>TANAW Team</strong></p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Hi ${businessName},

        Your password has been successfully changed!

        This is a confirmation that your TANAW account password was recently changed.

        If you did not make this change, please contact our support team immediately.

        Best regards,
        TANAW Team
      `,
    };

    await transporter.sendMail(mailOptions);
    console.log("✅ Password reset confirmation email sent to:", email);
  } catch (error) {
    console.error("❌ Error sending confirmation email:", error);
    // Don't throw error here - password was already reset successfully
  }
};

