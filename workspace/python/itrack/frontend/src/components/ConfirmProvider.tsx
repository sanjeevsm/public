import React, { createContext, useCallback, useContext, useState, ReactNode } from 'react';

interface ConfirmOptions {
  title?: string;
  message: string;
}

type ConfirmFn = (opts: ConfirmOptions) => Promise<boolean>;

const ConfirmContext = createContext<ConfirmFn | undefined>(undefined);

export const ConfirmProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [pending, setPending] = useState<null | { opts: ConfirmOptions; resolve: (b: boolean) => void }>(null);

  const showConfirm = useCallback<ConfirmFn>((opts) => {
    return new Promise<boolean>((resolve) => {
      setPending({ opts, resolve });
    });
  }, []);

  const handle = (val: boolean) => {
    if (pending) {
      pending.resolve(val);
      setPending(null);
    }
  };

  return (
    <ConfirmContext.Provider value={showConfirm}>
      {children}
      {pending && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" />
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 z-10 w-11/12 max-w-md">
            <h3 className="text-lg font-bold mb-2">{pending.opts.title ?? 'Confirm'}</h3>
            <p className="mb-4">{pending.opts.message}</p>
            <div className="flex justify-end gap-2">
              <button onClick={() => handle(false)} className="btn btn-secondary">Cancel</button>
              <button onClick={() => handle(true)} className="btn btn-primary">Confirm</button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
};

export const useConfirm = () => {
  const ctx = useContext(ConfirmContext);
  if (!ctx) throw new Error('useConfirm must be used inside ConfirmProvider');
  return ctx;
};

export default ConfirmProvider;
