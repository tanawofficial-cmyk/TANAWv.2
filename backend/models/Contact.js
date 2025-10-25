import mongoose from "mongoose";

const contactSchema = new mongoose.Schema({
  name: { 
    type: String, 
    required: true,
    trim: true
  },
  email: { 
    type: String, 
    required: true,
    trim: true,
    lowercase: true
  },
  subject: { 
    type: String, 
    required: true,
    trim: true
  },
  message: { 
    type: String, 
    required: true
  },
  status: {
    type: String,
    enum: ['new', 'in_progress', 'resolved', 'closed'],
    default: 'new'
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'urgent'],
    default: 'medium'
  },
  respondedAt: {
    type: Date
  },
  createdAt: { 
    type: Date, 
    default: Date.now 
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// Index for faster queries
contactSchema.index({ email: 1, createdAt: -1 });
contactSchema.index({ status: 1 });

export default mongoose.model("Contact", contactSchema);

