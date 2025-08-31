export default function ApprovalButtons({ onApprove, onReject, isLoading }) {
  return (
    <div style={{
      display: 'flex',
      gap: '15px',
      justifyContent: 'center',
      margin: '20px 0',
      fontFamily: '"Inter", "Segoe UI", Roboto, sans-serif'
    }}>
      <button
        onClick={onApprove}
        disabled={isLoading}
        style={{
          padding: '12px 24px',
          background: isLoading 
            ? 'linear-gradient(45deg, #6b7280, #4b5563)' 
            : 'linear-gradient(45deg, #22c55e, #16a34a)',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          opacity: isLoading ? 0.7 : 1,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: isLoading 
            ? '0 3px 8px rgba(107, 114, 128, 0.3)'
            : '0 6px 18px rgba(34, 197, 94, 0.4)',
          transition: 'all 0.3s ease',
          fontFamily: 'inherit'
        }}
      >
        {isLoading ? (
          <>
            <div style={{
              width: '16px',
              height: '16px',
              border: '2px solid #ffffff',
              borderTop: '2px solid transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
            Posting...
          </>
        ) : (
          <>
            ✅ Approve & Post
          </>
        )}
      </button>

      <button
        onClick={onReject}
        disabled={isLoading}
        style={{
          padding: '12px 24px',
          background: isLoading 
            ? 'linear-gradient(45deg, #6b7280, #4b5563)' 
            : 'linear-gradient(45deg, #ef4444, #dc2626)',
          color: 'white',
          border: 'none',
          borderRadius: '10px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          opacity: isLoading ? 0.7 : 1,
          boxShadow: isLoading 
            ? '0 3px 8px rgba(107, 114, 128, 0.3)'
            : '0 6px 18px rgba(239, 68, 68, 0.4)',
          transition: 'all 0.3s ease',
          fontFamily: 'inherit'
        }}
      >
        ❌ Reject
      </button>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
