import mongoose from "mongoose";

const fileSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  filename: { type: String, required: true },
  originalname: { type: String },
  uploadDate: { type: Date, default: Date.now },
  status: { type: String, default: "pending" }, // e.g., pending, processed
});

export default mongoose.model("File", fileSchema);
