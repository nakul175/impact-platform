-- Register frozen analysis packages and versioned learning-agenda records.
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check
    FROM pg_constraint
   WHERE conrelid='impact.object_registry'::regclass
     AND conname='object_registry_object_type_check';
  IF position('AnalysisPackage' IN original_check)=0 THEN
    ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
    EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
      || regexp_replace(original_check,'\)$',
        ' OR object_type IN (''AnalysisPackage'',''AnalysisResultReference'',''LearningQuestion'',''LearningApplicabilityReview''))');
  END IF;
END $$;

CREATE POLICY worker_analysis_learning_registry_fence
  ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
  USING(object_type NOT IN ('AnalysisPackage','AnalysisResultReference','LearningQuestion','LearningApplicabilityReview'))
  WITH CHECK(object_type NOT IN ('AnalysisPackage','AnalysisResultReference','LearningQuestion','LearningApplicabilityReview'));
CREATE POLICY worker_analysis_learning_revision_fence
  ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
  USING(object_type NOT IN ('AnalysisPackage','AnalysisResultReference','LearningQuestion','LearningApplicabilityReview'))
  WITH CHECK(object_type NOT IN ('AnalysisPackage','AnalysisResultReference','LearningQuestion','LearningApplicabilityReview'));

COMMIT;
