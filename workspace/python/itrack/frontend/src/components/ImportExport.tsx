import React, { useState } from 'react';
import { Download, Upload } from 'lucide-react';
import { transactionService } from '../services/transactionService';

interface Props {
  onImportSuccess: () => void;
}

export const ImportExport: React.FC<Props> = ({ onImportSuccess }) => {
  const [isImporting, setIsImporting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [importMessage, setImportMessage] = useState('');

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const blob = await transactionService.exportTransactions();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `transactions_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export transactions');
    } finally {
      setIsExporting(false);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setImportMessage('');

    try {
      const result = await transactionService.importTransactions(file);
      
      let message = `Successfully imported ${result.imported} transactions.`;
      if (result.failed > 0) {
        message += ` ${result.failed} failed.`;
        if (result.errors.length > 0) {
          message += `\n\nErrors:\n${result.errors.join('\n')}`;
        }
      }
      
      setImportMessage(message);
      onImportSuccess();
    } catch (error: any) {
      setImportMessage(error.response?.data?.detail || 'Import failed');
    } finally {
      setIsImporting(false);
      // Reset file input
      event.target.value = '';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={handleExport}
          disabled={isExporting}
          className="btn btn-primary flex items-center justify-center space-x-2 flex-1 disabled:opacity-50"
        >
          <Download size={18} />
          <span>{isExporting ? 'Exporting...' : 'Export CSV'}</span>
        </button>

        <label className="btn btn-secondary flex items-center justify-center space-x-2 flex-1 cursor-pointer">
          <Upload size={18} />
          <span>{isImporting ? 'Importing...' : 'Import CSV'}</span>
          <input
            type="file"
            accept=".csv"
            onChange={handleImport}
            disabled={isImporting}
            className="hidden"
          />
        </label>
      </div>

      {importMessage && (
        <div className={`p-3 rounded-md text-sm ${
          importMessage.includes('Successfully') 
            ? 'bg-green-50 text-green-800 border border-green-200'
            : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          <pre className="whitespace-pre-wrap">{importMessage}</pre>
        </div>
      )}

      <div className="text-xs text-gray-500">
        <p className="font-medium mb-1">CSV Format:</p>
        <code className="block bg-gray-100 p-2 rounded">
          description,amount,type,category,date<br />
          "Salary",5000,income,"Salary",2024-01-15<br />
          "Groceries",150.50,expense,"Food & Dining",2024-01-16
        </code>
      </div>
    </div>
  );
};
