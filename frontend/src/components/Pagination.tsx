import React from "react";
import { Button } from "@/components/Button";
import "@/styles/components.css";

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ page, pageSize, total, onChange }) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const canPrev = page > 1;
  const canNext = page < totalPages;

  return (
    <div className="pagination">
      <Button tone="ghost" size="sm" disabled={!canPrev} onClick={() => onChange(page - 1)}>
        上一页
      </Button>
      <span className="pagination__meta">
        第 {page} / {totalPages} 页 · 共 {total} 条
      </span>
      <Button tone="ghost" size="sm" disabled={!canNext} onClick={() => onChange(page + 1)}>
        下一页
      </Button>
    </div>
  );
};
