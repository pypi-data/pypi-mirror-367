/**
 * @type {import('node-pg-migrate').ColumnDefinitions | undefined}
 */
export const shorthands = undefined;

/**
 * @param pgm {import('node-pg-migrate').MigrationBuilder}
 * @param run {() => void | undefined}
 * @returns {Promise<void> | void}
 */
export const up = (pgm) => {
  // Create function to handle new user signup
  pgm.sql(`
    CREATE OR REPLACE FUNCTION public.handle_new_user_quota()
    RETURNS trigger
    LANGUAGE plpgsql
    SECURITY DEFINER
    SET search_path = public
    AS $$
    DECLARE
      new_quota_id uuid;
    BEGIN
      -- Create quota for new user
      INSERT INTO quotas (id, user_id, quota_type, monthly_limit)
      VALUES (gen_random_uuid(), NEW.id, 'cloud-run-minutes', 500)
      RETURNING id INTO new_quota_id;

      RETURN NEW;
    END;
    $$;
  `);

  // Create trigger on auth.users
  pgm.sql(`
    CREATE TRIGGER on_auth_user_created
      AFTER INSERT ON auth.users
      FOR EACH ROW
      EXECUTE FUNCTION public.handle_new_user_quota();
  `);
};

/**
 * @param pgm {import('node-pg-migrate').MigrationBuilder}
 * @param run {() => void | undefined}
 * @returns {Promise<void> | void}
 */
export const down = (pgm) => {
  // Drop trigger first
  pgm.sql('DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users');
  
  // Drop function
  pgm.sql('DROP FUNCTION IF EXISTS public.handle_new_user_quota()');
}; 