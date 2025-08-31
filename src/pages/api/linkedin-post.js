// API route to handle LinkedIn posting
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  let { text } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Post text is required' });
  }

  // Add timestamp to prevent duplicates
  const timestamp = new Date().toLocaleString();
  text = `${text}\n\n📅 Posted on ${timestamp}`;

  try {
    // LinkedIn API configuration
    const ACCESS_TOKEN = process.env.ACCESS_TOKEN;
    const ORG_URN = process.env.PERSON_URN;

    if (!ACCESS_TOKEN || !ORG_URN) {
      return res.status(500).json({ 
        error: 'LinkedIn credentials not configured. Check environment variables.' 
      });
    }

    const headers = {
      "Authorization": `Bearer ${ACCESS_TOKEN}`,
      "Content-Type": "application/json",
      "X-Restli-Protocol-Version": "2.0.0"
    };

    const payload = {
      "author": ORG_URN,
      "lifecycleState": "PUBLISHED",
      "specificContent": {
        "com.linkedin.ugc.ShareContent": {
          "shareCommentary": { "text": text },
          "shareMediaCategory": "NONE"
        }
      },
      "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
      }
    };

    const response = await fetch("https://api.linkedin.com/v2/ugcPosts", {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.ok) {
      console.log('✅ SUCCESS: LinkedIn post published!');
      console.log('   Post ID:', data.id);
      console.log('   View at: https://www.linkedin.com/feed/update/' + data.id + '/');
      return res.status(200).json({ 
        success: true, 
        message: 'Post published successfully!',
        linkedinResponse: data,
        postId: data.id,
        postUrl: `https://www.linkedin.com/feed/update/${data.id}/`
      });
    } else {
      // Clean, simple error logging
      console.log('❌ FAILED: LinkedIn post failed');
      console.log(`   Status: ${response.status}`);
      
      if (response.status === 422 && data.message && data.message.includes('duplicate')) {
        console.log('   Reason: Duplicate content detected');
        console.log('   💡 TIP: The post content was too similar to a previous post');
      } else if (response.status === 401) {
        console.log('   Reason: Access token invalid/expired');
        console.log('   💡 TIP: Generate a new access token in LinkedIn Developer Portal');
      } else {
        console.log(`   Reason: ${data.message || 'Unknown error'}`);
      }
      
      return res.status(400).json({ 
        error: 'Failed to post to LinkedIn',
        details: data,
        statusCode: response.status
      });
    }

  } catch (error) {
    console.log('🚨 SERVER ERROR: Something went wrong');
    console.log(`   Error: ${error.message}`);
    console.log(`   💡 TIP: Check your environment variables are set correctly`);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error.message
    });
  }
}
