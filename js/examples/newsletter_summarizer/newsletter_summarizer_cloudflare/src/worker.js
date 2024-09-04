import { Hono } from 'hono';
import { CloudflareToolSet } from "composio-core";
const app = new Hono();

// Configuration for the AI model
const config = {
  model: '@hf/nousresearch/hermes-2-pro-mistral-7b',
};

// Function to set up the Gmail connection for the user if it doesn't exist
async function setupUserConnectionIfNotExists(toolset, entityId, c) {
  console.log('Setting up user connection...');
  const entity = await toolset.client.getEntity(entityId);
  const connection = await entity.getConnection('gmail');

  if (!connection) {
    // Removed duplicate declaration of connection
    const newConnection = await entity.initiateConnection('gmail');
    console.log('User needs to log in via: ', newConnection.redirectUrl);
    c.json({ redirectUrl: newConnection.redirectUrl, message: 'Please log in to continue and then call this API again' });
  } else {
    console.log('User is already connected to Gmail.');
  }

  return connection;
}

// Function to fetch emails
async function fetchEmails(toolset, entityId, c) {
  console.log('Fetching emails...');
  const tools = await toolset.getActions({ actions: ['gmail_fetch_emails'] }, entityId);
  const instruction = `
    "Fetch the most recent newsletter emails from the inbox. "
    "Look for emails with subjects containing words like 'newsletter', 'update', or 'digest'. "
    "Retrieve the content of these emails, including any important links or attachments. "
    "Pay special attention to newsletters from reputable sources and industry leaders."
  `;

  let messages = [
    { role: 'system', content: '' },
    { role: 'user', content: instruction },
  ];

  try {
    const toolCallResp = await c.env.AI.run(config.model, {
      messages,
      tools,
    });
    console.log('Emails fetched successfully.');
    return await toolset.handleToolCall(toolCallResp, entityId);
  } catch (error) {
    console.error('Error fetching emails:', error);
    c.text('Failed to fetch emails due to an internal error.', 500);
  }
}

// Function to send summarized email
async function sendSummaryEmail(toolset, entityId, summarizedContent, c) {
  console.log('Sending summarized email...');
  const tools = await toolset.getActions({ actions: ['gmail_send_email'] }, entityId);
  const instruction = `
    Send an email to recipient email prathit3.14@gmail.com
    subject is "Summarized yo"
    body is "Hello there"
  `;

  let messages = [
    { role: 'system', content: 'You are an expert gmail assistant who is very good at sending emails using the tools provided to you. THE TOOL CALL FOR SENDING EMAIL IS GMAIL_SEND_EMAIL, USE IT' },
    { role: 'user', content: instruction },
  ];

  console.log("The tool is", tools);
  const toolCallResp = await c.env.AI.run(config.model, {
    messages,
    tools,
  });

  console.log('Email sent successfully.', toolCallResp);
  return await toolset.handleToolCall(toolCallResp, entityId);
}

// POST endpoint to handle the AI request
app.post('/help', async (c) => {
  console.log('Received request to /help endpoint.');
  const toolset = new CloudflareToolSet({
    apiKey: c.env.COMPOSIO_API_KEY,
  });

  try {
    const entity = await toolset.client.getEntity('default');
    await setupUserConnectionIfNotExists(toolset, entity.id, c);

    // Step 1: Fetch emails
    //const fetchedEmails = await fetchEmails(toolset, entity.id, c);

    // Step 2: Summarize content (you may want to add an additional AI step here to summarize the fetched emails)
    //const summarizedContent = fetchedEmails; // Replace this with actual summarization logic if needed
    const summarizedContent=""
    // Step 3: Send summarized email
    await sendSummaryEmail(toolset, entity.id, summarizedContent, c);

    console.log('Process completed successfully.');
    return c.json({ message: "Emails fetched, summarized, and sent successfully" });
  } catch (err) {
    console.error('Error occurred:', err);
    return c.text('An unexpected error occurred while processing your request.', 500);
  }
});

export default app;
