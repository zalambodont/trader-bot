import { toast } from 'react-toastify';

// Success toast
export const showSuccess = (message) => {
  toast.success(message, {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  });
};

// Error toast
export const showError = (message) => {
  toast.error(message, {
    position: "top-right",
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  });
};

// Warning toast
export const showWarning = (message) => {
  toast.warning(message, {
    position: "top-right",
    autoClose: 4000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  });
};

// Info toast
export const showInfo = (message) => {
  toast.info(message, {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  });
};

// Confirm dialog with toast
export const showConfirm = (message, onConfirm, onCancel) => {
  const toastId = toast.info(
    <div>
      <div style={{ marginBottom: '12px', fontSize: '14px' }}>{message}</div>
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
        <button
          onClick={() => {
            toast.dismiss(toastId);
            if (onCancel) onCancel();
          }}
          style={{
            padding: '6px 16px',
            background: '#6b7280',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: '600'
          }}
        >
          Cancel
        </button>
        <button
          onClick={() => {
            toast.dismiss(toastId);
            if (onConfirm) onConfirm();
          }}
          style={{
            padding: '6px 16px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '13px',
            fontWeight: '600'
          }}
        >
          Confirm
        </button>
      </div>
    </div>,
    {
      position: "top-center",
      autoClose: false,
      hideProgressBar: true,
      closeOnClick: false,
      closeButton: false,
      draggable: false,
    }
  );
};
