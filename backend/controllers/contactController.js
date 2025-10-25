import Contact from "../models/Contact.js";
import { sendContactNotificationEmail, sendContactConfirmationEmail } from "../services/emailService.js";

// Submit contact form
export const submitContactForm = async (req, res) => {
  try {
    const { name, email, subject, message } = req.body;

    // Validate required fields
    if (!name || !email || !subject || !message) {
      return res.status(400).json({
        success: false,
        message: "All fields are required"
      });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        success: false,
        message: "Please provide a valid email address"
      });
    }

    // Create contact message
    const contact = new Contact({
      name,
      email,
      subject,
      message,
      status: 'new',
      priority: 'medium'
    });

    await contact.save();

    // Send notification email to admin (don't wait for it)
    sendContactNotificationEmail(contact)
      .catch(err => console.error("Error sending admin notification:", err));

    // Send confirmation email to user (don't wait for it)
    sendContactConfirmationEmail(email, name)
      .catch(err => console.error("Error sending user confirmation:", err));

    res.status(201).json({
      success: true,
      message: "Thank you for contacting us! We'll get back to you within 24 hours.",
      data: {
        id: contact._id,
        createdAt: contact.createdAt
      }
    });
  } catch (error) {
    console.error("Error submitting contact form:", error);
    res.status(500).json({
      success: false,
      message: "Failed to submit contact form. Please try again later."
    });
  }
};

// Get all contact messages (Admin only)
export const getAllContactMessages = async (req, res) => {
  try {
    const { status, priority, limit = 50, page = 1 } = req.query;

    const query = {};
    if (status) query.status = status;
    if (priority) query.priority = priority;

    const skip = (page - 1) * limit;

    const contacts = await Contact.find(query)
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip(skip);

    const total = await Contact.countDocuments(query);

    res.json({
      success: true,
      data: {
        contacts,
        pagination: {
          total,
          page: parseInt(page),
          limit: parseInt(limit),
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    console.error("Error fetching contact messages:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch contact messages"
    });
  }
};

// Update contact message status (Admin only)
export const updateContactStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const { status, priority } = req.body;

    const updateData = { updatedAt: new Date() };
    if (status) updateData.status = status;
    if (priority) updateData.priority = priority;

    if (status === 'resolved' || status === 'closed') {
      updateData.respondedAt = new Date();
    }

    const contact = await Contact.findByIdAndUpdate(
      id,
      updateData,
      { new: true }
    );

    if (!contact) {
      return res.status(404).json({
        success: false,
        message: "Contact message not found"
      });
    }

    res.json({
      success: true,
      message: "Contact status updated successfully",
      data: contact
    });
  } catch (error) {
    console.error("Error updating contact status:", error);
    res.status(500).json({
      success: false,
      message: "Failed to update contact status"
    });
  }
};

// Delete contact message (Admin only)
export const deleteContactMessage = async (req, res) => {
  try {
    const { id } = req.params;

    const contact = await Contact.findByIdAndDelete(id);

    if (!contact) {
      return res.status(404).json({
        success: false,
        message: "Contact message not found"
      });
    }

    res.json({
      success: true,
      message: "Contact message deleted successfully"
    });
  } catch (error) {
    console.error("Error deleting contact message:", error);
    res.status(500).json({
      success: false,
      message: "Failed to delete contact message"
    });
  }
};

// Get contact statistics (Admin only)
export const getContactStats = async (req, res) => {
  try {
    const total = await Contact.countDocuments();
    const newMessages = await Contact.countDocuments({ status: 'new' });
    const inProgress = await Contact.countDocuments({ status: 'in_progress' });
    const resolved = await Contact.countDocuments({ status: 'resolved' });

    // Get messages from last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentMessages = await Contact.countDocuments({
      createdAt: { $gte: thirtyDaysAgo }
    });

    res.json({
      success: true,
      data: {
        total,
        newMessages,
        inProgress,
        resolved,
        recentMessages
      }
    });
  } catch (error) {
    console.error("Error fetching contact stats:", error);
    res.status(500).json({
      success: false,
      message: "Failed to fetch contact statistics"
    });
  }
};

