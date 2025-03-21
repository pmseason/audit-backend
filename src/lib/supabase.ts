// eslint-disable-next-line import/no-extraneous-dependencies
import { createClient } from '@supabase/supabase-js';


export const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!,
);