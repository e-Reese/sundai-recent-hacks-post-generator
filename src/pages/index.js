import { useState } from 'react';
import PostPreview from '../components/PostPreview';
import ApprovalButtons from '../components/ApprovalButtons';

export default function Home() {
  const [postData, setPostData] = useState({
    text: "🚀 Success! Automated LinkedIn post!",
    status: "pending" // pending, approved, rejected
  });

  const [isPosting, setIsPosting] = useState(false);
  const [result, setResult] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState("");
  const [linkedinPostUrl, setLinkedinPostUrl] = useState(null);
  const [postHistory, setPostHistory] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleApprove = async () => {
    setIsPosting(true);
    try {
      const response = await fetch('/api/linkedin-post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: postData.text }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setPostData({ ...postData, status: 'approved' });
        setResult({ success: true, message: 'Post published successfully!' });
        
        // Extract LinkedIn post URL from response
        let postUrl = null;
        if (data.linkedinResponse && data.linkedinResponse.id) {
          const postId = data.linkedinResponse.id;
          postUrl = `https://www.linkedin.com/feed/update/${postId}/`;
          setLinkedinPostUrl(postUrl);
        }
        
        // Add to post history
        const historyItem = {
          id: Date.now(),
          text: postData.text,
          timestamp: new Date(),
          url: postUrl,
          status: 'success'
        };
        setPostHistory(prev => [historyItem, ...prev]);
        
      } else {
        setResult({ success: false, message: data.error || 'Failed to post' });
        
        // Add failed post to history
        const historyItem = {
          id: Date.now(),
          text: postData.text,
          timestamp: new Date(),
          url: null,
          status: 'failed',
          error: data.error
        };
        setPostHistory(prev => [historyItem, ...prev]);
      }
    } catch (error) {
      setResult({ success: false, message: 'Network error occurred' });
    }
    setIsPosting(false);
  };

  const handleReject = () => {
    setPostData({ ...postData, status: 'rejected' });
    setResult({ success: false, message: 'Post rejected' });
  };

  const resetPost = () => {
    setPostData({ ...postData, status: 'pending' });
    setResult(null);
    setLinkedinPostUrl(null);
  };

  const handleEditStart = () => {
    setEditText(postData.text);
    setIsEditing(true);
  };

  const handleEditSave = () => {
    setPostData({ ...postData, text: editText });
    setIsEditing(false);
  };

  const handleEditCancel = () => {
    setEditText("");
    setIsEditing(false);
  };

  const handleGeneratePost = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/generate-post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ date: selectedDate }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setPostData({ text: data.generatedPost, status: 'pending' });
        setResult({ success: true, message: 'Post generated successfully!' });
      } else {
        setResult({ success: false, message: data.error || 'Failed to generate post' });
      }
    } catch (error) {
      setResult({ success: false, message: 'Failed to generate post' });
    }
    setIsGenerating(false);
  };

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: '"Inter", "Segoe UI", Roboto, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      <div style={{ 
        maxWidth: '900px', 
        margin: '0 auto', 
        padding: '40px 20px',
        color: 'white'
      }}>
        <h1 style={{
          fontSize: '3rem',
          fontWeight: '700',
          textAlign: 'center',
          marginBottom: '10px',
          background: 'linear-gradient(45deg, #fff, #e0e7ff)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Sundai Hacks Weekly Summary Post Generator
        </h1>
        <p style={{
          textAlign: 'center',
          fontSize: '1.2rem',
          opacity: '0.9',
          marginBottom: '40px',
          fontWeight: '300'
        }}>
          Review, approve, and publish your LinkedIn content
        </p>

        {/* Date Filter and Generate Section */}
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          padding: '30px',
          margin: '30px 0',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#1f2937',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            🎯 Generate Post from Sundai Hack Projects
          </h3>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <label style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151'
              }}>
                📅 Select Date:
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                style={{
                  padding: '12px 16px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '12px',
                  fontSize: '15px',
                  fontFamily: 'inherit',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  minWidth: '160px'
                }}
                onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
              />
            </div>
            
            <button
              onClick={handleGeneratePost}
              disabled={isGenerating}
              style={{
                padding: '14px 28px',
                background: isGenerating 
                  ? 'linear-gradient(45deg, #6b7280, #4b5563)' 
                  : 'linear-gradient(45deg, #10b981, #059669)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                cursor: isGenerating ? 'not-allowed' : 'pointer',
                fontSize: '16px',
                fontWeight: '600',
                opacity: isGenerating ? 0.7 : 1,
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                boxShadow: isGenerating 
                  ? '0 4px 12px rgba(107, 114, 128, 0.3)'
                  : '0 8px 24px rgba(16, 185, 129, 0.4)',
                transition: 'all 0.3s ease',
                fontFamily: 'inherit',
                marginTop: '20px'
              }}
            >
              {isGenerating ? (
                <>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid #ffffff',
                    borderTop: '2px solid transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite'
                  }}></div>
                  Generating...
                </>
              ) : (
                <>
                  ✨ Generate Post
                </>
              )}
            </button>
          </div>
          
          <div style={{
            marginTop: '15px',
            textAlign: 'center',
            fontSize: '13px',
            color: '#6b7280'
          }}>
            Generate a LinkedIn post based on Sundai Hack projects from the selected date
          </div>
        </div>
      
      {isEditing ? (
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
          <h3 style={{
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#1f2937',
            marginBottom: '20px'
          }}>
            ✏️ Edit Post
          </h3>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            placeholder="Write your LinkedIn post..."
            style={{
              width: '100%',
              minHeight: '150px',
              padding: '20px',
              border: '2px solid #e5e7eb',
              borderRadius: '12px',
              fontSize: '15px',
              fontFamily: 'inherit',
              lineHeight: '1.6',
              resize: 'vertical',
              outline: 'none',
              transition: 'border-color 0.3s ease',
              boxSizing: 'border-box'
            }}
            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
            onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
          />
          <div style={{
            display: 'flex',
            gap: '15px',
            justifyContent: 'flex-end',
            marginTop: '20px'
          }}>
            <button
              onClick={handleEditCancel}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(45deg, #6b7280, #4b5563)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                fontFamily: 'inherit'
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleEditSave}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(45deg, #3b82f6, #1d4ed8)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                fontFamily: 'inherit'
              }}
            >
              Save Changes
            </button>
          </div>
        </div>
      ) : (
      <PostPreview 
        text={postData.text}
        status={postData.status}
          onEdit={handleEditStart}
          canEdit={postData.status === 'pending'}
      />
      )}
      
      {postData.status === 'pending' && !isEditing && (
        <ApprovalButtons
          onApprove={handleApprove}
          onReject={handleReject}
          isLoading={isPosting}
        />
      )}
      
      {result && (
        <div style={{
          padding: '20px',
          margin: '30px 0',
          borderRadius: '16px',
          backgroundColor: result.success ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: result.success ? '#22c55e' : '#ef4444',
          border: `2px solid ${result.success ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          backdropFilter: 'blur(10px)',
          fontSize: '1.1rem',
          fontWeight: '500',
          textAlign: 'center',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ marginBottom: linkedinPostUrl ? '15px' : '0' }}>
            {result.success ? '🎉 ' : '⚠️ '}{result.message}
          </div>
          {linkedinPostUrl && result.success && (
            <div>
              <a
                href={linkedinPostUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '12px 20px',
                  background: 'linear-gradient(45deg, #0077b5, #005885)',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  boxShadow: '0 4px 12px rgba(0, 119, 181, 0.3)',
                  transition: 'all 0.3s ease',
                  fontFamily: 'inherit'
                }}
                onMouseOver={(e) => {
                  e.target.style.transform = 'translateY(-1px)';
                  e.target.style.boxShadow = '0 6px 16px rgba(0, 119, 181, 0.4)';
                }}
                onMouseOut={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 4px 12px rgba(0, 119, 181, 0.3)';
                }}
              >
                🔗 View on LinkedIn
              </a>
            </div>
          )}
        </div>
      )}
      
      {postData.status !== 'pending' && (
        <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <button 
          onClick={resetPost}
          style={{
              padding: '16px 32px',
              background: 'linear-gradient(45deg, #3b82f6, #1d4ed8)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '1.1rem',
              fontWeight: '600',
              boxShadow: '0 8px 24px rgba(59, 130, 246, 0.4)',
              transition: 'all 0.3s ease',
              fontFamily: 'inherit'
            }}
            onMouseOver={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 12px 32px rgba(59, 130, 246, 0.5)';
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 8px 24px rgba(59, 130, 246, 0.4)';
            }}
          >
            ✨ Create New Post
          </button>
        </div>
      )}

      {/* Post History Section */}
      {postHistory.length > 0 && (
        <div style={{
          marginTop: '50px',
          padding: '30px',
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '20px',
          backdropFilter: 'blur(10px)'
        }}>
          <h2 style={{
            fontSize: '1.5rem',
            fontWeight: '700',
            color: 'white',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            📊 Session History ({postHistory.length} posts)
          </h2>
          
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '15px',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            {postHistory.map((post) => (
              <div
                key={post.id}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                  padding: '15px 20px',
                  borderRadius: '12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: '14px',
                    color: '#374151',
                    marginBottom: '5px',
                    fontWeight: '500',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}>
                    {post.text.length > 100 ? post.text.substring(0, 100) + '...' : post.text}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: '#6b7280',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    <span>{post.timestamp.toLocaleTimeString()}</span>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '8px',
                      fontSize: '11px',
                      fontWeight: '600',
                      backgroundColor: post.status === 'success' ? '#22c55e' : '#ef4444',
                      color: 'white'
                    }}>
                      {post.status === 'success' ? '✅ Posted' : '❌ Failed'}
                    </span>
                  </div>
                </div>
                
                {post.url && (
                  <a
                    href={post.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '8px 12px',
                      background: 'linear-gradient(45deg, #0077b5, #005885)',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: '600',
                      marginLeft: '15px'
                    }}
                  >
                    🔗 View
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
