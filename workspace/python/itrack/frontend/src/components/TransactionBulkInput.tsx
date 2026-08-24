import React, { useState, useRef } from 'react';
import { transactionService } from '../services/transactionService';

interface Row {
  description: string;
  amount: number | '';
  type: 'income' | 'expense';
  category: string;
  date: string;
}

export const TransactionBulkInput: React.FC<{ onDone?: () => void; defaultType?: 'income' | 'expense' }> = ({ onDone, defaultType = 'expense' }) => {
  const [rows, setRows] = useState<Row[]>([
    { description: '', amount: '', type: defaultType, category: '', date: new Date().toISOString().split('T')[0] },
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const updateRow = (index: number, patch: Partial<Row>) => {
    const copy = [...rows];
    copy[index] = { ...copy[index], ...patch } as Row;
    setRows(copy);
  };

  const addRow = () => setRows([...rows, { description: '', amount: '', type: defaultType, category: '', date: new Date().toISOString().split('T')[0] }]);
  const removeRow = (index: number) => setRows(rows.filter((_, i) => i !== index));

  const [csvPreview, setCsvPreview] = useState<Row[] | null>(null);
  const [parsedRows, setParsedRows] = useState<Row[] | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const pasteAreaRef = useRef<HTMLTextAreaElement | null>(null);

  const parseCsvText = (text: string): Row[] => {
    const lines = text.trim().split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
    const result: Row[] = [];
    for (const line of lines) {
      // Support comma or tab separated values
      const parts = line.includes('\t') ? line.split('\t') : line.split(',');
      const [description, amount, type, category, date] = parts.map((p) => p.replace(/^\"|\"$/g, '').trim());
      result.push({
        description: description || '',
        amount: amount ? parseFloat(amount) : '',
        type: (type === 'income' ? 'income' : 'expense') as 'income' | 'expense',
        category: category || '',
        date: date || new Date().toISOString().split('T')[0],
      });
    }
    return result;
  };

  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      const text = String(reader.result || '');
      const rows = parseCsvText(text);
      setCsvPreview(rows.slice(0, 20));
      setParsedRows(rows);
      setMessage(`Preview ${rows.length} rows`);
    };
    reader.readAsText(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    handleFileUpload(file);
  };

  const handlePasteParse = () => {
    const text = pasteAreaRef.current?.value || '';
    if (!text) return;
    const rows = parseCsvText(text);
    setParsedRows(rows);
    setMessage(`Parsed ${rows.length} rows from paste`);
  };

  const handleSubmit = async () => {
    setMessage(null);
    setIsSubmitting(true);
    try {
      const toSend = (parsedRows && parsedRows.length > 0 ? parsedRows : rows).map((r) => ({
        description: r.description,
        amount: typeof r.amount === 'number' ? r.amount : parseFloat(String(r.amount || '0')),
        type: r.type,
        category: r.category,
        date: new Date(r.date).toISOString(),
        mode: 'private' as const,
      }));

      const result = await transactionService.bulkCreate(toSend);
      setMessage(`Inserted ${result.inserted}, failed ${result.failed}`);
      if (onDone) onDone();
      // clear parsed rows and table
      setParsedRows(null);
      setCsvPreview(null);
      setRows([{ description: '', amount: '', type: defaultType, category: '', date: new Date().toISOString().split('T')[0] }]);
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Failed to import rows');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-3">Bulk Excel-style Input</h3>
      {message && <div className="mb-3 p-2 bg-green-50 rounded">{message}</div>}
      <div className="mb-3">
        <div className="flex space-x-2 items-center mb-2">
          <label className="text-sm">Upload CSV:</label>
          <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileChange} />
          <button type="button" onClick={() => { fileInputRef.current && fileInputRef.current.click(); }} className="btn btn-ghost">Select File</button>
        </div>
        <div className="mb-2">
          <label className="text-sm">Or paste tab/comma-separated rows from Excel/Sheets:</label>
          <div className="flex space-x-2 mt-1">
            <textarea ref={pasteAreaRef} rows={3} className="input flex-1" placeholder={'Description\tAmount\tType(income|expense)\tCategory\tDate (YYYY-MM-DD)'} />
            <div className="flex flex-col">
              <button type="button" onClick={handlePasteParse} className="btn btn-secondary mb-2">Parse Paste</button>
              <button type="button" onClick={() => { pasteAreaRef.current && (pasteAreaRef.current.value = ''); setParsedRows(null); }} className="btn btn-ghost">Clear</button>
            </div>
          </div>
        </div>
        {csvPreview && (
          <div className="mb-2">
            <p className="text-sm text-gray-600">CSV Preview (first {csvPreview.length} rows):</p>
            <div className="overflow-auto border rounded p-2 bg-white">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-gray-500"><th className="p-1">Description</th><th className="p-1">Amount</th><th className="p-1">Type</th><th className="p-1">Category</th><th className="p-1">Date</th></tr>
                </thead>
                <tbody>
                  {csvPreview.map((r, i) => (
                    <tr key={i}><td className="p-1">{r.description}</td><td className="p-1">{r.amount}</td><td className="p-1">{r.type}</td><td className="p-1">{r.category}</td><td className="p-1">{r.date}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <div className="overflow-auto">
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="text-left text-sm text-gray-600">
              <th className="p-2">Description</th>
              <th className="p-2">Amount</th>
              <th className="p-2">Type</th>
              <th className="p-2">Category</th>
              <th className="p-2">Date</th>
              <th className="p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={idx} className="border-t">
                <td className="p-2">
                  <input value={r.description} onChange={(e) => updateRow(idx, { description: e.target.value })} className="input" />
                </td>
                <td className="p-2 w-32">
                  <input type="number" value={r.amount as any} onChange={(e) => updateRow(idx, { amount: e.target.value === '' ? '' : parseFloat(e.target.value) })} className="input" />
                </td>
                <td className="p-2 w-36">
                  <select value={r.type} onChange={(e) => updateRow(idx, { type: e.target.value as any })} className="input">
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                </td>
                <td className="p-2">
                  <input value={r.category} onChange={(e) => updateRow(idx, { category: e.target.value })} className="input" />
                </td>
                <td className="p-2 w-40">
                  <input type="date" value={r.date} onChange={(e) => updateRow(idx, { date: e.target.value })} className="input" />
                </td>
                <td className="p-2">
                  <button type="button" onClick={() => removeRow(idx)} className="btn btn-ghost text-red-600">Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex space-x-2 mt-3">
        <button onClick={addRow} className="btn btn-secondary">Add Row</button>
          <button onClick={handleSubmit} disabled={isSubmitting} className="btn btn-primary">{isSubmitting ? 'Importing...' : 'Import Rows'}</button>
      </div>
    </div>
  );
};

export default TransactionBulkInput;
