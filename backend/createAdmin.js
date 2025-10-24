// createAdmin.js
import mongoose from "mongoose";
import bcrypt from "bcryptjs";
import dotenv from "dotenv";
import User from "./models/User.js";

// Load environment variables
dotenv.config();

// Admin credentials
const adminData = {
  fullName: "TANAW Admin",
  businessName: "TANAW Headquarters",
  email: "admin@tanawofficial.com",
  password: "TANAW2025Admin!", // New secure admin password
  role: "admin",
  status: "active",
};

const createAdmin = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log("Connected to MongoDB");

    // Check if admin already exists and delete if found
    const existingAdmin = await User.findOne({ email: adminData.email });
    if (existingAdmin) {
      console.log("Existing admin found, deleting old admin...");
      await User.deleteOne({ email: adminData.email });
      console.log("Old admin deleted successfully!");
    }

    // Hash the password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(adminData.password, salt);

    // Create admin user
    const adminUser = new User({
      ...adminData,
      password: hashedPassword,
    });

    await adminUser.save();
    console.log("Admin user created successfully!");
    process.exit(0);
  } catch (error) {
    console.error("Error creating admin:", error);
    process.exit(1);
  }
};

createAdmin();
