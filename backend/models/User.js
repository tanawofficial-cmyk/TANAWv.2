//User.js Model

import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  fullName: { 
    type: String, 
    required: true, 
    trim: true 
  },
  email: { 
    type: String, 
    required: true, 
    unique: true,
    lowercase: true,
    trim: true,
  },
  password: { type: String, required: true },
  role: { type: String, enum: ["user", "admin"], default: "user" },
  licenseKey: { type: String, default: null },
  businessName: { 
    type: String, 
    required: true, 
    trim: true 
  },
  resetPasswordToken: { type: String, default: null },
  resetPasswordExpires: { type: Date, default: null },
  // Email change verification fields
  pendingEmail: { type: String, default: null },
  emailVerificationToken: { type: String, default: null },
  emailVerificationExpires: { type: Date, default: null },
}, { timestamps: true });

// ✅ Virtual field for "profile" (business name + email only)
userSchema.virtual("profile").get(function () {
  return {
    businessName: this.businessName,
    email: this.email,
  };
});

// ✅ Ensure virtuals are included when converting to JSON
userSchema.set("toJSON", { virtuals: true });
userSchema.set("toObject", { virtuals: true });

export default mongoose.model("User", userSchema);
