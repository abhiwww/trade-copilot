import React from "react";
import { motion } from "framer-motion";
import { FileText, X, RefreshCw, CheckCircle2 } from "lucide-react";
import { Badge } from "../../ui/atomic";

interface UploadedFile {
  id: string;
  filename: string;
  status: "Uploading" | "Processing" | "Processed" | "Failed";
  size: string;
}

export default function FileUploadBadge({
  file,
  onRemove
}: {
  file: UploadedFile;
  onRemove: (id: string) => void;
}) {
  const statusConfig = {
    Uploading: { icon: <RefreshCw size={10} className="animate-spin text-slate-400" />, variant: "default" },
    Processing: { icon: <RefreshCw size={10} className="animate-spin text-[#A1844D]" />, variant: "default" },
    Processed: { icon: <CheckCircle2 size={10} className="text-green-600" />, variant: "success" },
    Failed: { icon: <X size={10} className="text-rose-600" />, variant: "error" },
  } as const;

  const { icon, variant } = statusConfig[file.status];

  return (
    <Badge variant={variant}>
      <FileText size={12} className="text-[#A1844D]" />
      <span className="max-w-[120px] truncate">{file.filename}</span>
      <span className="text-[10px] text-slate-400">{file.size}</span>
      {icon}
      <button onClick={() => onRemove(file.id)} className="ml-1 hover:text-rose-600 transition-colors">
        <X size={12} />
      </button>
    </Badge>
  );
}
