export default function PostPreview({ text, status, onEdit, canEdit }) {
  const getStatusColor = () => {
    switch (status) {
      case 'approved': return '#28a745';
      case 'rejected': return '#dc3545';
      default: return '#ffc107';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'approved': return '✅ Approved & Posted';
      case 'rejected': return '❌ Rejected';
      default: return '⏳ Pending Approval';
    }
  };

  return (
    <div style={{
      border: 'none',
      borderRadius: '20px',
      padding: '30px',
      margin: '30px 0',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(20px)',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)',
      fontFamily: '"Inter", "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '25px'
      }}>
        <h3 style={{
          fontSize: '1.5rem',
          fontWeight: '700',
          color: '#1f2937',
          margin: '0'
        }}>
          LinkedIn Post Preview
        </h3>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {canEdit && (
            <button
              onClick={onEdit}
              style={{
                padding: '8px 16px',
                background: 'linear-gradient(45deg, #f59e0b, #d97706)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)',
                fontFamily: 'inherit'
              }}
            >
              ✏️ Edit
            </button>
          )}
          <span style={{
            padding: '8px 16px',
            borderRadius: '20px',
            backgroundColor: getStatusColor(),
            color: 'white',
            fontSize: '14px',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
          }}>
            {getStatusText()}
          </span>
        </div>
      </div>
      
      <div style={{
        backgroundColor: 'white',
        padding: '25px',
        borderRadius: '16px',
        border: 'none',
        minHeight: '120px',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.06)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          marginBottom: '10px'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #0077b5, #005885)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: '700',
            marginRight: '15px',
            boxShadow: '0 4px 12px rgba(0, 119, 181, 0.3)'
          }}>
            YC
          </div>
          <div>
            <div style={{ 
              fontWeight: '600', 
              fontSize: '16px',
              color: '#1f2937'
            }}>
              Your Company
            </div>
            <div style={{ 
              fontSize: '14px', 
              color: '#6b7280',
              fontWeight: '400'
            }}>
              Just now • 🌐 Public
            </div>
          </div>
        </div>
        
        <div style={{
          lineHeight: '1.6',
          fontSize: '15px',
          whiteSpace: 'pre-wrap',
          color: '#374151',
          fontWeight: '400'
        }}>
          {text}
        </div>
      </div>
    </div>
  );
}
