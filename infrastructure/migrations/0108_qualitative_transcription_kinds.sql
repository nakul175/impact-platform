-- Register governed qualitative coding, processing destinations and transcription artifacts.
BEGIN;
SET LOCAL ROLE impact_owner;

DO $$
DECLARE original_check text;
BEGIN
  SELECT pg_get_constraintdef(oid) INTO STRICT original_check
    FROM pg_constraint
   WHERE conrelid='impact.object_registry'::regclass
     AND conname='object_registry_object_type_check';
  IF position('QualitativeCodebook' IN original_check)=0 THEN
    ALTER TABLE impact.object_registry DROP CONSTRAINT object_registry_object_type_check;
    EXECUTE 'ALTER TABLE impact.object_registry ADD CONSTRAINT object_registry_object_type_check '
      || regexp_replace(original_check,'\)$',
        ' OR object_type IN (''QualitativeCodebook'',''QualitativeCodingAssignment'',''QualitativeAdjudication'',''QualitativeAgreement'',''ProcessingDestination'',''TranscriptArtifact'',''QuotationReference''))');
  END IF;
END $$;

CREATE POLICY worker_qualitative_transcription_registry_fence
  ON impact.object_registry AS RESTRICTIVE FOR ALL TO impact_worker
  USING(object_type NOT IN ('QualitativeCodebook','QualitativeCodingAssignment','QualitativeAdjudication','QualitativeAgreement','ProcessingDestination','TranscriptArtifact','QuotationReference'))
  WITH CHECK(object_type NOT IN ('QualitativeCodebook','QualitativeCodingAssignment','QualitativeAdjudication','QualitativeAgreement','ProcessingDestination','TranscriptArtifact','QuotationReference'));
CREATE POLICY worker_qualitative_transcription_revision_fence
  ON impact.object_revision AS RESTRICTIVE FOR ALL TO impact_worker
  USING(object_type NOT IN ('QualitativeCodebook','QualitativeCodingAssignment','QualitativeAdjudication','QualitativeAgreement','ProcessingDestination','TranscriptArtifact','QuotationReference'))
  WITH CHECK(object_type NOT IN ('QualitativeCodebook','QualitativeCodingAssignment','QualitativeAdjudication','QualitativeAgreement','ProcessingDestination','TranscriptArtifact','QuotationReference'));

COMMIT;
