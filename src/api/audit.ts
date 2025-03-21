import express from 'express';
import { SearchConfig, SearchResult, startAudit, getSupportedSources, testConnection, checkRoleOpen } from '@pmseason/ai-job-scraper';
import { supabase } from '../lib/supabase';


const router = express.Router();

type AuditInput = {
  remoteUrl?: string;
  searchConfigs: SearchConfig[]
};

type AuditResult = {
  status: 'not-started' | 'running' | 'completed'
  error?: string;
  message?: string;
  data?: SearchResult[]
};

// https://github.com/puppeteer/puppeteer/issues/2242

const auditMap = new Map<string, AuditResult>();

router.post('/start', async (req, res) => {

  try {
    //read body
    const { remoteUrl, searchConfigs } = req.body as AuditInput;

    //test connection to make sure we have a chrome connection
    const connected = await testConnection(remoteUrl);

    if (!connected) {
      return res.status(400).json({
        message: 'Not connected to Chrome',
      });
    }

    // start audit
    const auditId = Math.random().toString(36).substring(7);

    // save client random id in client map
    auditMap.set(auditId, { status: 'running' });

    // start audit, once done set result in map
    startAudit(searchConfigs, remoteUrl)
      .then((result) => {
        auditMap.set(auditId, { status: 'completed', message: 'SUCCESS', data: result });
      }).catch((err) => {
        console.error(err);
        auditMap.set(auditId, { status: 'completed', error: err });
      });
    res.json({
      message: 'Audit started',
      id: auditId,
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({
      message: 'Internal Server Error',
    });
  }
});

router.get('/:auditId/status', (req, res) => {
  // read client id from path
  const auditId = req.params.auditId;

  // get result from map
  const result = auditMap.get(auditId);

  //check if invalid audit
  if (!result) {
    return res.status(404).json({
      message: 'Invalid ID',
    });
  }

  //extract result status
  res.json(result);

  //if completed without error, wipe from memory
  const { status, error } = result;
  if (status === 'completed' && !error) {
    auditMap.delete(auditId);
  }


});

router.get('/supported', (req, res) => {
  const sources = getSupportedSources();
  res.json(sources);
});

router.post('/checkOpen', async (req, res) => {
  try {
    //read body
    const { applicationUrl } = req.body as { applicationUrl: string };

    //check open
    const result = await checkRoleOpen(applicationUrl);

    //return
    res.json(result);
  } catch (error) {
    console.error(error);
    res.status(500).json({
      message: 'Internal Server Error',
    });
  }
});

router.get('/openRoles', async (req, res) => {
  const { data, error } = await supabase
    .from('positions')
    .select('*, company(*)')
    .order('dateAdded', { ascending: false })
    .eq('hidden', false)
    .eq('status', 'open');

  if (error) {
    return res.status(400).json({
      message: 'Error while fetching jobs from supabase',
    });
  }

  return res.json(data);
});

router.get('/test', async (req, res) => {
  const { remoteUrl } = req.body;

  //test connection to make sure we have a chrome connection
  const connected = await testConnection(remoteUrl);

  if (connected) {
    res.status(200).json({
      message: 'Connected to Chrome',
    });
  } else {
    res.status(400).json({
      message: 'Not connected to Chrome',
    });
  }
});

export default router;
