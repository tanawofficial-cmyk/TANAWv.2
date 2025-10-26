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

// Send contact form notification to admin
export const sendContactNotificationEmail = async (contact) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransporter({
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

    const adminEmail = process.env.ADMIN_EMAIL || "tanawofficial@gmail.com";

    const mailOptions = {
      from: `"TANAW Contact Form" <${process.env.EMAIL_FROM || "noreply@tanaw.com"}>`,
      to: adminEmail,
      subject: `New Contact Message: ${contact.subject}`,
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .info-box { background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea; }
            .message-box { background: white; padding: 20px; margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📬 New Contact Message</h1>
            </div>
            <div class="content">
              <h2>Contact Details</h2>
              <div class="info-box">
                <p><strong>Name:</strong> ${contact.name}</p>
                <p><strong>Email:</strong> <a href="mailto:${contact.email}">${contact.email}</a></p>
                <p><strong>Subject:</strong> ${contact.subject}</p>
                <p><strong>Date:</strong> ${new Date(contact.createdAt).toLocaleString()}</p>
              </div>
              
              <h3>Message:</h3>
              <div class="message-box">
                ${contact.message.replace(/\n/g, '<br>')}
              </div>
              
              <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                To respond, reply directly to this email or contact ${contact.name} at ${contact.email}
              </p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        New Contact Message from TANAW
        
        Name: ${contact.name}
        Email: ${contact.email}
        Subject: ${contact.subject}
        Date: ${new Date(contact.createdAt).toLocaleString()}
        
        Message:
        ${contact.message}
        
        Reply to: ${contact.email}
      `,
      replyTo: contact.email
    };

    const info = await transporter.sendMail(mailOptions);

    if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVICE) {
      console.log("📧 Preview URL:", nodemailer.getTestMessageUrl(info));
    }

    console.log("✅ Contact notification email sent to admin");
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error("❌ Error sending contact notification email:", error);
    throw new Error("Failed to send contact notification email");
  }
};

// Send email change verification email
export const sendEmailChangeVerificationEmail = async (newEmail, verificationToken, userName) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransporter({
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

    const verificationUrl = `${process.env.FRONTEND_URL || "http://localhost:3000"}/verify-email/${verificationToken}`;

    const mailOptions = {
      from: `"TANAW Support" <${process.env.EMAIL_FROM || "noreply@tanaw.com"}>`,
      to: newEmail,
      subject: "Verify Your New Email Address - TANAW",
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
            .info { background: #e3f2fd; border-left: 4px solid #2196f3; padding: 12px; margin: 20px 0; }
            .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📧 Verify Your Email Change</h1>
            </div>
            <div class="content">
              <p>Hi <strong>${userName}</strong>,</p>
              
              <p>You requested to change your email address on TANAW. To complete this change, please verify your new email address by clicking the button below:</p>
              
              <div style="text-align: center;">
                <a href="${verificationUrl}" class="button">Verify Email Address</a>
              </div>
              
              <p>Or copy and paste this link into your browser:</p>
              <p style="word-break: break-all; color: #667eea;">${verificationUrl}</p>
              
              <div class="info">
                <strong>🔒 Security Information:</strong>
                <ul style="margin: 10px 0;">
                  <li>This link will expire in <strong>24 hours</strong></li>
                  <li>If you didn't request this change, please ignore this email</li>
                  <li>Your email address will remain unchanged</li>
                  <li>After verification, we'll notify your old email address</li>
                </ul>
              </div>
              
              <p>Need help? Contact our support team at tanawofficial@gmail.com</p>
              
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
        Hi ${userName},

        You requested to change your email address on TANAW. To complete this change, please verify your new email address by clicking this link:
        
        ${verificationUrl}
        
        This link will expire in 24 hours.
        
        If you didn't request this change, please ignore this email. Your email address will remain unchanged.
        
        Best regards,
        TANAW Team
      `,
    };

    const info = await transporter.sendMail(mailOptions);

    if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVICE) {
      console.log("📧 Preview URL:", nodemailer.getTestMessageUrl(info));
    }

    console.log("✅ Email verification sent to:", newEmail);
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error("❌ Error sending email verification:", error);
    throw new Error("Failed to send email verification");
  }
};

// Send email change notification to old email
export const sendEmailChangeNotificationEmail = async (oldEmail, userName, newEmail) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransporter({
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
      from: `"TANAW Security" <${process.env.EMAIL_FROM || "noreply@tanaw.com"}>`,
      to: oldEmail,
      subject: "Your Email Address Was Changed - TANAW",
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🔔 Email Address Changed</h1>
            </div>
            <div class="content">
              <p>Hi <strong>${userName}</strong>,</p>
              
              <p>This is a security notification to inform you that your email address for your TANAW account has been successfully changed.</p>
              
              <div class="warning">
                <strong>📧 New Email Address:</strong><br>
                ${newEmail}
              </div>
              
              <p><strong>⚠️ Important:</strong> Future account notifications will be sent to your new email address.</p>
              
              <p>If you did not make this change, your account may have been compromised. Please contact our support team immediately at tanawofficial@gmail.com</p>
              
              <p>Best regards,<br>
              <strong>TANAW Security Team</strong></p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Hi ${userName},

        This is a security notification to inform you that your email address for your TANAW account has been successfully changed.

        New Email Address: ${newEmail}

        Important: Future account notifications will be sent to your new email address.

        If you did not make this change, your account may have been compromised. Please contact our support team immediately at tanawofficial@gmail.com

        Best regards,
        TANAW Security Team
      `,
    };

    await transporter.sendMail(mailOptions);
    console.log("✅ Email change notification sent to old email:", oldEmail);
  } catch (error) {
    console.error("❌ Error sending email change notification:", error);
    // Don't throw error here - email was already changed
  }
};

// Send account deletion notification
export const sendAccountDeletionEmail = async (email, userName) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransporter({
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
      subject: "Your TANAW Account Has Been Deleted",
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .warning { background: #fee2e2; border-left: 4px solid #dc2626; padding: 12px; margin: 20px 0; }
            .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>🚫 Account Deleted</h1>
            </div>
            <div class="content">
              <p>Hi <strong>${userName}</strong>,</p>
              
              <p>We're writing to inform you that your TANAW account has been deleted by an administrator.</p>
              
              <div class="warning">
                <strong>⚠️ Important Information:</strong>
                <ul style="margin: 10px 0;">
                  <li>Your account and all associated data have been removed</li>
                  <li>You will no longer be able to access TANAW services</li>
                  <li>All uploaded datasets have been deleted</li>
                  <li>This action cannot be undone</li>
                </ul>
              </div>
              
              <p><strong>Why was my account deleted?</strong></p>
              <ul>
                <li>Violation of Terms of Service</li>
                <li>Account inactive for extended period</li>
                <li>User request</li>
                <li>Administrative decision</li>
              </ul>
              
              <p>If you believe this was done in error or have questions, please contact our support team at <strong>tanawofficial@gmail.com</strong></p>
              
              <p>We appreciate your time using TANAW.</p>
              
              <p>Best regards,<br>
              <strong>TANAW Team</strong></p>
            </div>
            <div class="footer">
              <p>&copy; ${new Date().getFullYear()} TANAW. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Hi ${userName},

        We're writing to inform you that your TANAW account has been deleted by an administrator.

        Important Information:
        - Your account and all associated data have been removed
        - You will no longer be able to access TANAW services
        - All uploaded datasets have been deleted
        - This action cannot be undone

        If you believe this was done in error or have questions, please contact our support team at tanawofficial@gmail.com

        Best regards,
        TANAW Team
      `,
    };

    await transporter.sendMail(mailOptions);
    console.log("✅ Account deletion email sent to:", email);
  } catch (error) {
    console.error("❌ Error sending account deletion email:", error);
    // Don't throw error - account was already deleted
  }
};

// Send welcome email on registration
export const sendWelcomeEmail = async (email, userName, businessName) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransporter({
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

    const mailOptions = {
      from: `"TANAW Team" <${process.env.EMAIL_FROM || "noreply@tanaw.com"}>`,
      to: email,
      subject: "Welcome to TANAW - Your Analytics Journey Begins! 🎉",
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .button { display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }
            .feature-box { background: white; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; border-radius: 5px; }
            .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #666; }
            .emoji { font-size: 48px; margin: 10px 0; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <div class="emoji">🎉</div>
              <h1 style="margin: 10px 0; font-size: 32px;">Welcome to TANAW!</h1>
              <p style="font-size: 18px; margin: 10px 0; opacity: 0.95;">Transform Your Data into Insights</p>
            </div>
            <div class="content">
              <p>Hi <strong>${userName}</strong>,</p>
              
              <p style="font-size: 18px; color: #667eea; font-weight: bold;">🎊 Congratulations! Your TANAW account is ready!</p>
              
              <p>We're thrilled to have <strong>${businessName}</strong> join our community of data-driven businesses. You now have access to powerful analytics tools that will transform how you understand your data.</p>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}/login" class="button">Get Started Now →</a>
              </div>
              
              <h3 style="color: #667eea; margin-top: 30px;">✨ What You Can Do With TANAW:</h3>
              
              <div class="feature-box">
                <strong>📊 Upload & Analyze Data</strong>
                <p style="margin: 5px 0; color: #666;">Upload CSV/Excel files and get instant insights with AI-powered analytics</p>
              </div>
              
              <div class="feature-box">
                <strong>📈 Generate Smart Charts</strong>
                <p style="margin: 5px 0; color: #666;">Auto-generate beautiful, interactive visualizations tailored to your data</p>
              </div>
              
              <div class="feature-box">
                <strong>🤖 AI-Powered Forecasting</strong>
                <p style="margin: 5px 0; color: #666;">Predict future trends with advanced machine learning models</p>
              </div>
              
              <div class="feature-box">
                <strong>💡 Actionable Insights</strong>
                <p style="margin: 5px 0; color: #666;">Get narrative explanations and recommendations from our AI</p>
              </div>
              
              <h3 style="color: #667eea; margin-top: 30px;">🚀 Quick Start Guide:</h3>
              <ol style="color: #666;">
                <li><strong>Login</strong> to your dashboard</li>
                <li><strong>Upload</strong> your first dataset (CSV or Excel)</li>
                <li><strong>View</strong> auto-generated charts and insights</li>
                <li><strong>Explore</strong> forecasts and analytics</li>
                <li><strong>Download</strong> reports for sharing</li>
              </ol>
              
              <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong>💼 Your Account Details:</strong><br>
                <strong>Business:</strong> ${businessName}<br>
                <strong>Email:</strong> ${email}<br>
                <strong>Account Type:</strong> Standard User
              </div>
              
              <p style="margin-top: 30px;">Need help getting started? Check out our <a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}/docs" style="color: #667eea;">documentation</a> or reply to this email with any questions.</p>
              
              <p style="margin-top: 30px;">We're here to help you succeed! 🌟</p>
              
              <p>Best regards,<br>
              <strong>The TANAW Team</strong></p>
            </div>
            <div class="footer">
              <p>This is an automated welcome message from TANAW.</p>
              <p>&copy; ${new Date().getFullYear()} TANAW. All rights reserved.</p>
              <p style="margin-top: 10px;">
                <a href="tanawofficial@gmail.com" style="color: #667eea; text-decoration: none;">Contact Support</a> | 
                <a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}/docs" style="color: #667eea; text-decoration: none;">Documentation</a>
              </p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Welcome to TANAW, ${userName}!

        Congratulations! Your TANAW account for ${businessName} is ready!

        What You Can Do With TANAW:
        - Upload & Analyze Data: Upload CSV/Excel files and get instant insights
        - Generate Smart Charts: Auto-generate beautiful visualizations
        - AI-Powered Forecasting: Predict future trends with ML models
        - Actionable Insights: Get narrative explanations from our AI

        Quick Start Guide:
        1. Login to your dashboard
        2. Upload your first dataset (CSV or Excel)
        3. View auto-generated charts and insights
        4. Explore forecasts and analytics
        5. Download reports for sharing

        Your Account Details:
        Business: ${businessName}
        Email: ${email}
        Account Type: Standard User

        Get started now: ${process.env.FRONTEND_URL || 'http://localhost:3000'}/login

        Need help? Reply to this email or visit our documentation.

        Best regards,
        The TANAW Team
      `,
    };

    const info = await transporter.sendMail(mailOptions);

    if (process.env.NODE_ENV === "development" || !process.env.EMAIL_SERVICE) {
      console.log("📧 Preview URL:", nodemailer.getTestMessageUrl(info));
    }

    console.log("✅ Welcome email sent to:", email);
    return { success: true, messageId: info.messageId };
  } catch (error) {
    console.error("❌ Error sending welcome email:", error);
    // Don't throw error - user was already registered
  }
};

// Send contact confirmation to user
export const sendContactConfirmationEmail = async (email, name) => {
  try {
    let transporter = createTransporter();

    if (!transporter) {
      const testAccount = await nodemailer.createTestAccount();
      transporter = nodemailer.createTransporter({
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
      subject: "We received your message - TANAW Support",
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
            .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #666; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>✉️ Message Received!</h1>
            </div>
            <div class="content">
              <p>Hi <strong>${name}</strong>,</p>
              
              <div class="success">
                <strong>Thank you for contacting TANAW!</strong>
              </div>
              
              <p>We've received your message and our support team will review it shortly.</p>
              
              <p><strong>What happens next?</strong></p>
              <ul>
                <li>Our team will review your message within 24 hours</li>
                <li>You'll receive a response via email</li>
                <li>For urgent issues, we prioritize based on severity</li>
              </ul>
              
              <p>In the meantime, you might find these resources helpful:</p>
              <ul>
                <li><a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}/docs">Documentation</a></li>
                <li><a href="${process.env.FRONTEND_URL || 'http://localhost:3000'}/support">Support Center</a></li>
              </ul>
              
              <p>Best regards,<br>
              <strong>TANAW Support Team</strong></p>
            </div>
            <div class="footer">
              <p>This is an automated confirmation from TANAW.</p>
              <p>&copy; ${new Date().getFullYear()} TANAW. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Hi ${name},
        
        Thank you for contacting TANAW!
        
        We've received your message and our support team will review it shortly.
        
        What happens next?
        - Our team will review your message within 24 hours
        - You'll receive a response via email
        - For urgent issues, we prioritize based on severity
        
        Best regards,
        TANAW Support Team
      `,
    };

    await transporter.sendMail(mailOptions);
    console.log("✅ Contact confirmation email sent to:", email);
  } catch (error) {
    console.error("❌ Error sending contact confirmation email:", error);
    // Don't throw error here - contact was already saved
  }
};

