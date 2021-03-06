#!/usr/bin/python

'''
Validates Manifest file under the security-content repo for correctness.
'''

import glob
import json
import jsonschema
import yaml
import sys
import argparse
from os import path


def validate_detection_contentv2(detection, DETECTION_UUIDS, errors, macros, lookups):

    if detection['id'] == '':
        errors.append('ERROR: Blank ID')

    if detection['id'] in DETECTION_UUIDS:
        errors.append('ERROR: Duplicate UUID found: %s' % detection['id'])
    else:
        DETECTION_UUIDS.append(detection['id'])

    if detection['name'].endswith(" "):
        errors.append(
            "ERROR: Detection name has trailing spaces: '%s'" %
            detection['name'])

    try:
        detection['description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    if 'how_to_implement' in detection:
        try:
            detection['how_to_implement'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: how_to_implement not ascii")

    if 'eli5' in detection:
        try:
            detection['eli5'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: eli5 not ascii")

    if 'known_false_positives' in detection:
        try:
            detection['known_false_positives'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: known_false_positives not ascii")
    # modded to pass validation for uba detections - not yet fleshed out
    if 'splunk' in detection['detect']:
        # do a regex match here instead of key values
        # if (detection['detect']['splunk']['correlation_rule']['search'].find('tstats') != -1) or \
        #        (detection['detect']['splunk']['correlation_rule']['search'].find('datamodel') != -1):
        if (detection['detect']['splunk']['correlation_rule']['search'].find('datamodel') != -1):
            if 'data_models' not in detection['data_metadata']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' field is not set")

            if not detection['data_metadata']['data_models']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' is empty")

        # do a regex match here instead of key values
        if (detection['detect']['splunk']['correlation_rule']['search'].find('sourcetype') != -1):
            if 'data_sourcetypes' not in detection['data_metadata']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but 'data_sourcetypes' field is not set")
            elif not detection['data_metadata']['data_sourcetypes']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but 'data_sourcetypes' is empty")

        if 'macros' in detection['detect']['splunk']['correlation_rule']:
            for macro in detection['detect']['splunk']['correlation_rule']['macros']:
                if macro not in macros:
                    errors.append("ERROR: The Splunk search specifies a macro \"{}\" but there is no macro manifest for it".format(macro))

        if 'lookups' in detection['detect']['splunk']['correlation_rule']:
            for lookup in detection['detect']['splunk']['correlation_rule']['lookups']:
                if lookup not in lookups:
                    errors.append("ERROR: The Splunk search specifies a lookup \"{}\" but there is no lookup manifest for it".format(lookup))


        if 'notable' in  detection['detect']['splunk']['correlation_rule']:
            if ('drilldown_search' in detection['detect']['splunk']['correlation_rule']['notable']) ^ \
                    ('drilldown_name' in detection['detect']['splunk']['correlation_rule']['notable']):

                errors.append("ERROR: Both drilldown_search and drilldown_name must be defined")

    elif 'uba' in detection['detect']:
        if (detection['detect']['uba']['correlation_rule']['search'].find('tstats') != -1) or \
                (detection['detect']['splunk']['correlation_rule']['search'].find('datamodel') != -1):

            if 'data_models' not in detection['data_metadata']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' field is not set")

            if not detection['data_metadata']['data_models']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' is empty")

        # do a regex match here instead of key values
        if (detection['detect']['uba']['correlation_rule']['search'].find('sourcetype') != -1):
            if 'data_sourcetypes' not in detection['data_metadata']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but 'data_sourcetypes' \
                            field is not set")

            if not detection['data_metadata']['data_sourcetypes']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but \
                        'data_sourcetypes' is empty")

        # do a regex match here instead of key values

    return errors


def validate_investigation_contentv2(investigation, investigation_uuids, errors, macros, lookups):

    if investigation['id'] == '':
        errors.append('ERROR: Blank ID')

    if investigation['id'] in investigation_uuids:
        errors.append('ERROR: Duplicate UUID found: %s' % investigation['id'])
    else:
        investigation_uuids.append(investigation['id'])

    if investigation['name'].endswith(" "):
        errors.append(
            "ERROR: Investigation name has trailing spaces: '%s'" %
            investigation['name'])

    try:
        investigation['description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    if 'how_to_implement' in investigation:
        try:
            investigation['how_to_implement'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: how_to_implement not ascii")

    if 'eli5' in investigation:
        try:
            investigation['eli5'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: eli5 not ascii")

    if 'known_false_positives' in investigation:
        try:
            investigation['known_false_positives'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: known_false_positives not ascii")

    if 'splunk' in investigation['investigate']:

        # do a regex match here instead of key values
        if (investigation['investigate']['splunk']['search'].find('tstats') != -1) or \
                (investigation['investigate']['splunk']['search'].find('datamodel') != -1):

            if 'data_models' not in investigation['data_metadata']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' field is not set")

            if not investigation['data_metadata']['data_models']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' is empty")

        # do a regex match here instead of key values
        if (investigation['investigate']['splunk']['search'].find('sourcetype') != -1):
            if 'data_sourcetypes' not in investigation['data_metadata']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but 'data_sourcetypes' \
                            field is not set")

            if not investigation['data_metadata']['data_sourcetypes']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but \
                        'data_sourcetypes' is empty")

        if 'macros' in investigation['investigate']['splunk']:
            for macro in investigation['investigate']['splunk']['macros']:
                if macro not in macros:
                    errors.append("ERROR: The Splunk search specifies a macro \"{}\" but there is no macro manifest for it".format(macro))

        if 'lookups' in investigation['investigate']['splunk']:
            for lookup in investigation['investigate']['splunk']['lookups']:
                if lookup not in lookups:
                    errors.append("ERROR: The Splunk search specifies a lookup \"{}\" but there is no lookup manifest for it".format(lookup))


    return errors


def validate_baselines_contentv2(baseline, baselines_uuids, errors, macros, lookups):

    if baseline['id'] == '':
        errors.append('ERROR: Blank ID')

    if baseline['id'] in baselines_uuids:
        errors.append('ERROR: Duplicate UUID found: %s' % baseline['id'])
    else:
        baselines_uuids.append(baseline['id'])

    if baseline['name'].endswith(" "):
        errors.append(
            "ERROR: Investigation name has trailing spaces: '%s'" %
            baseline['name'])

    try:
        baseline['description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    if 'how_to_implement' in baseline:
        try:
            baseline['how_to_implement'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: how_to_implement not ascii")

    if 'eli5' in baseline:
        try:
            baseline['eli5'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: eli5 not ascii")

    if 'known_false_positives' in baseline:
        try:
            baseline['known_false_positives'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: known_false_positives not ascii")

    if 'splunk' in baseline['baseline']:

        # do a regex match here instead of key values
        if (baseline['baseline']['splunk']['search'].find('tstats') != -1) or \
                (baseline['baseline']['splunk']['search'].find('datamodel') != -1):

            if 'data_models' not in baseline['data_metadata']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' field is not set")

            if not baseline['data_metadata']['data_models']:
                errors.append("ERROR: The Splunk search uses a data model but 'data_models' is empty")

        # do a regex match here instead of key values
        if (baseline['baseline']['splunk']['search'].find('sourcetype') != -1):
            if 'data_sourcetypes' not in baseline['data_metadata']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but 'data_sourcetypes' \
                            field is not set")

            if not baseline['data_metadata']['data_sourcetypes']:
                errors.append("ERROR: The Splunk search specifies a sourcetype but \
                        'data_sourcetypes' is empty")

        if 'macros' in baseline['baseline']['splunk']:
            for macro in baseline['baseline']['splunk']['macros']:
                if macro not in macros:
                    errors.append("ERROR: The Splunk search specifies a macro \"{}\" but there is no macro manifest for it".format(macro))

        if 'lookups' in baseline['baseline']['splunk']:
            for lookup in baseline['baseline']['splunk']['lookups']:
                if lookup not in lookups:
                    errors.append("ERROR: The Splunk search specifies a lookup \"{}\" but there is no lookup manifest for it".format(lookup))



    return errors


def validate_detection_contentv1(detection, DETECTION_UUIDS, errors):

    try:
        detection['search_description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    if detection['search_name'].endswith(" "):
        errors.append(
            "ERROR: Detection name has trailing spaces: '%s'" %
            detection['search_name'])

    if detection['search_id'] == '':
        errors.append('ERROR: Blank ID')

    if detection['search_id'] in DETECTION_UUIDS:
        errors.append('ERROR: Duplicate UUID found: %s' % detection['search_id'])
    else:
        DETECTION_UUIDS.append(detection['search_id'])

    if '| tstats' in detection['search'] or 'datamodel' in detection['search']:
        if 'data_models' not in detection['data_metadata']:
            errors.append(
                "ERROR: The search uses a data model but 'data_models' \
                        field is not set")

        if 'data_models' in detection and not \
                detection['data_metadata']['data_models']:
            errors.append(
                "ERROR: The search uses a data model but 'data_models' is empty")

    if 'sourcetype' in detection['search']:
        if 'data_sourcetypes' not in detection['data_metadata']:
            errors.append(
                "ERROR: The search specifies a sourcetype but 'data_sourcetypes' \
                        field is not set")

        if 'data_sourcetypes' in detection and not \
                detection['data_metadata']['data_sourcetypes']:
            errors.append(
                "ERROR: The search specifies a sourcetype but \
                        'data_sourcetypes' is empty")

    try:
        detection['search_description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: search_description not ascii")

    if 'how_to_implement' in detection:
        try:
            detection['how_to_implement'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: how_to_implement not ascii")

    if 'eli5' in detection:
        try:
            detection['eli5'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("eli5 not ascii")

    if 'known_false_positives' in detection:
        try:
            detection['known_false_positives'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: known_false_positives not ascii")

    if 'correlation_rule' in detection and 'notable' in \
            detection['correlation_rule']:
        try:
            detection['correlation_rule']['notable']['rule_title'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: rule_title not ascii")

        try:
            detection['correlation_rule']['notable']['rule_description'].encode(
                'ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: rule_description not ascii")

    return errors


def validate_investigation_contentv1(investigation, investigation_uuids, errors):

    try:
        investigation['search_description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    if investigation['search_name'].endswith(" "):
        errors.append(
            "ERROR: Investigation name has trailing spaces: '%s'" %
            investigation['search_name'])

    if investigation['search_id'] == '':
        errors.append('ERROR: Blank ID')

    if investigation['search_id'] in investigation_uuids:
        errors.append('ERROR: Duplicate UUID found: %s' % investigation['search_id'])
    else:
        investigation_uuids.append(investigation['search_id'])

    if '| tstats' in investigation['search'] or 'datamodel' in investigation['search']:
        if 'data_models' not in investigation['data_metadata']:
            errors.append(
                "ERROR: The search uses a data model but 'data_models' \
                        field is not set")

        if 'data_models' in investigation and not \
                investigation['data_metadata']['data_models']:
            errors.append(
                "ERROR: The search uses a data model but 'data_models' is empty")

    if 'sourcetype' in investigation['search']:
        if 'data_sourcetypes' not in investigation['data_metadata']:
            errors.append(
                "ERROR: The search specifies a sourcetype but 'data_sourcetypes' \
                        field is not set")

        if 'data_sourcetypes' in investigation and not \
                investigation['data_metadata']['data_sourcetypes']:
            errors.append(
                "ERROR: The search specifies a sourcetype but \
                        'data_sourcetypes' is empty")

    try:
        investigation['search_description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: search_description not ascii")

    if 'how_to_implement' in investigation:
        try:
            investigation['how_to_implement'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: how_to_implement not ascii")

    if 'eli5' in investigation:
        try:
            investigation['eli5'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("eli5 not ascii")

    if 'known_false_positives' in investigation:
        try:
            investigation['known_false_positives'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: known_false_positives not ascii")

    return errors


def validate_baselines_contentv1(baseline, baselines_uuids, errors):

    try:
        baseline['search_description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    if baseline['search_name'].endswith(" "):
        errors.append(
            "ERROR: Baseline name has trailing spaces: '%s'" %
            baseline['search_name'])

    if baseline['search_id'] == '':
        errors.append('ERROR: Blank ID')

    if baseline['search_id'] in baselines_uuids:
        errors.append('ERROR: Duplicate UUID found: %s' % baseline['search_id'])
    else:
        baselines_uuids.append(baseline['search_id'])

    if '| tstats' in baseline['search'] or 'datamodel' in baseline['search']:
        if 'data_models' not in baseline['data_metadata']:
            errors.append(
                "ERROR: The search uses a data model but 'data_models' \
                        field is not set")

        if 'data_models' in baseline and not \
                baseline['data_metadata']['data_models']:
            errors.append(
                "ERROR: The search uses a data model but 'data_models' is empty")

    if 'sourcetype' in baseline['search']:
        if 'data_sourcetypes' not in baseline['data_metadata']:
            errors.append(
                "ERROR: The search specifies a sourcetype but 'data_sourcetypes' \
                        field is not set")

        if 'data_sourcetypes' in baseline and not \
                baseline['data_metadata']['data_sourcetypes']:
            errors.append(
                "ERROR: The search specifies a sourcetype but \
                        'data_sourcetypes' is empty")

    try:
        baseline['search_description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: search_description not ascii")

    if 'how_to_implement' in baseline:
        try:
            baseline['how_to_implement'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: how_to_implement not ascii")

    if 'eli5' in baseline:
        try:
            baseline['eli5'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("eli5 not ascii")

    if 'known_false_positives' in baseline:
        try:
            baseline['known_false_positives'].encode('ascii')
        except UnicodeEncodeError:
            errors.append("ERROR: known_false_positives not ascii")

    return errors


def validate_investigation_content(investigation, investigation_uuids, macros, lookups):
    '''Validate that the content of a investigation manifest is correct'''
    errors = []

    # run v1 content validation
    if investigation["spec_version"] == 1:
        errors = validate_investigation_contentv1(investigation, investigation_uuids, errors)

    if investigation["spec_version"] == 2:
        errors = validate_investigation_contentv2(investigation, investigation_uuids, errors, macros, lookups)

    return errors


def validate_detection_content(detection, DETECTION_UUIDS, macros, lookups):
    '''Validate that the content of a detection manifest is correct'''
    errors = []

    # run v1 content validation
    if detection["spec_version"] == 1:
        errors = validate_detection_contentv1(detection, DETECTION_UUIDS, errors)

    if detection["spec_version"] == 2:
        errors = validate_detection_contentv2(detection, DETECTION_UUIDS, errors, macros, lookups)

    return errors


def validate_story_content(story, STORY_UUIDS):
    ''' Validate that the content of a story manifest is correct'''
    errors = []

    if story['id'] == '':
        errors.append('ERROR: Blank ID')

    if story['id'] in STORY_UUIDS:
        errors.append('ERROR: Duplicate UUID found: %s' % story['id'])
    else:
        STORY_UUIDS.append(story['id'])

    try:
        story['description'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: description not ascii")

    try:
        story['narrative'].encode('ascii')
    except UnicodeEncodeError:
        errors.append("ERROR: narrative not ascii")

    return errors


def validate_baselines_content(baseline, baselines_uuids, macros, lookups):
    '''Validate that the content of a baseline manifest is correct'''
    errors = []

    # run v1 content validation
    if baseline["spec_version"] == 1:
        errors = validate_baselines_contentv1(baseline, baselines_uuids, errors)

    if baseline["spec_version"] == 2:
        errors = validate_baselines_contentv2(baseline, baselines_uuids, errors, macros, lookups)

    return errors


def validate_investigation(REPO_PATH, verbose, macros, lookups):
    ''' Validates Investigation'''

    INVESTIGATION_UUIDS = []
    # retrive
    v1_schema_file_investigative = path.join(path.expanduser(REPO_PATH), 'spec/v1/investigative_search.json.spec')
    try:
        v1_schema_investigative = json.loads(open(v1_schema_file_investigative, 'rb').read())
    except IOError:
        print "ERROR: reading version 1 investigations schema file {0}".format(v1_schema_file_investigative)

    v1_schema_file_contexual = path.join(path.expanduser(REPO_PATH), 'spec/v1/contextual_search.json.spec')
    try:
        v1_schema_contexual = json.loads(open(v1_schema_file_contexual, 'rb').read())
    except IOError:
        print "ERROR: reading version 1 investigations schema file {0}".format(v1_schema_file_contexual)

    v2_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v2/investigations.spec.json')
    try:
        v2_schema = json.loads(open(v2_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 2 investigations schema file {0}".format(v2_schema_file)

    error = False
    manifest_files = path.join(path.expanduser(REPO_PATH), "investigations/*.yml")

    for manifest_file in glob.glob(manifest_files):
        if verbose:
            print "processing investigation {0}".format(manifest_file)

        # read in each investigation
        with open(manifest_file, 'r') as stream:
            try:
                investigation = list(yaml.safe_load_all(stream))[0]
            except yaml.YAMLError as exc:
                print(exc)
                print "Error reading {0}".format(manifest_file)
                error = True
                continue

        # validate v1 and v2 stories against spec for both investigations and old contexual searches

        if investigation['spec_version'] == 1 and investigation['search_type'] == "contextual":
            try:
                jsonschema.validate(instance=investigation, schema=v1_schema_contexual)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True
        elif investigation['spec_version'] == 1 and investigation['search_type'] == "investigative":
            try:
                jsonschema.validate(instance=investigation, schema=v1_schema_investigative)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True
        elif investigation['spec_version'] == 2:
            try:
                jsonschema.validate(instance=investigation, schema=v2_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True
        else:
            print "ERROR: Story {0} does not contain a spec_version which is required".format(manifest_file)
            error = True
            continue

        # now lets validate the content
        investigation_errors = validate_investigation_content(investigation, INVESTIGATION_UUIDS, macros, lookups)
        if investigation_errors:
            error = True
            for err in investigation_errors:
                print "{0} at:\n\t {1}".format(err, manifest_file)

    return error


def validate_detection(REPO_PATH, verbose, macros, lookups):
    ''' Validates Detections'''

    DETECTION_UUIDS = []
    # retrive
    v1_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v1/detection_search.json.spec')
    try:
        v1_schema = json.loads(open(v1_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 1 detection schema file {0}".format(v1_schema_file)
    except ValueError:
        print "ERROR: File is not proper JSON {0}".format(v1_schema_file)

    v2_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v2/detections.spec.json')
    try:
        v2_schema = json.loads(open(v2_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 2 detection schema file {0}".format(v2_schema_file)
    except ValueError:
        print "ERROR: File is not proper JSON {0}".format(v2_schema_file)

    error = False
    manifest_files = path.join(path.expanduser(REPO_PATH), "detections/*.yml")

    for manifest_file in glob.glob(manifest_files):
        if verbose:
            print "processing detection {0}".format(manifest_file)

        # read in each detection
        with open(manifest_file, 'r') as stream:
            try:
                detection = list(yaml.safe_load_all(stream))[0]
            except yaml.YAMLError as exc:
                print(exc)
                print "Error reading {0}".format(manifest_file)
                error = True
                continue

        # validate v1 and v2 stories against spec
        if detection['spec_version'] == 1:
            try:
                jsonschema.validate(instance=detection, schema=v1_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True

        elif detection['spec_version'] == 2:
            try:
                jsonschema.validate(instance=detection, schema=v2_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True

        else:
            print "ERROR: Story {0} does not contain a spec_version which is required".format(manifest_file)
            error = True
            continue

        # now lets validate the content
        detection_errors = validate_detection_content(detection, DETECTION_UUIDS, macros, lookups)
        if detection_errors:
            error = True
            for err in detection_errors:
                print "{0} at:\n\t {1}".format(err, manifest_file)

    return error


def validate_story(REPO_PATH, verbose):
    ''' Validates Stories'''

    STORY_UUIDS = []

    # retrive
    v1_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v1/analytic_story.json.spec')
    try:
        v1_schema = json.loads(open(v1_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 1 story schema file {0}".format(v1_schema_file)
    except ValueError:
        print "ERROR: File is not proper JSON {0}".format(v1_schema_file)

    v2_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v2/story.spec.json')
    try:
        v2_schema = json.loads(open(v2_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 2 story schema file {0}".format(v2_schema_file)
    except ValueError:
        print "ERROR: File is not proper JSON {0}".format(v2_schema_file)

    error = False
    story_manifest_files = path.join(path.expanduser(REPO_PATH), "stories/*.yml")

    for story_manifest_file in glob.glob(story_manifest_files):
        if verbose:
            print "processing story {0}".format(story_manifest_file)

        # read in each story
        with open(story_manifest_file, 'r') as stream:
            try:
                story = list(yaml.safe_load_all(stream))[0]
            except yaml.YAMLError as exc:
                print(exc)
                print "Error reading {0}".format(story_manifest_file)
                error = True
                continue

        # validate v1 and v2 stories against spec
        if story['spec_version'] == 1:
            try:
                jsonschema.validate(instance=story, schema=v1_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), story_manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True

        elif story['spec_version'] == 2:
            try:
                jsonschema.validate(instance=story, schema=v2_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), story_manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True

        else:
            print "ERROR: Story {0} does not contain a spec_version which is required".format(story_manifest_file)
            error = True
            continue

        # now lets validate the content
        story_errors = validate_story_content(story, STORY_UUIDS)
        if story_errors:
            error = True
            for err in story_errors:
                print "{0} at:\n\t {1}".format(err, story_manifest_file)

    return error


def validate_baselines(REPO_PATH, verbose, macros, lookups):
    ''' Validates Baselines'''

    BASELINE_UUIDS = []

    # retrive
    v1_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v1/support_search.json.spec')
    try:
        v1_schema = json.loads(open(v1_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 1 baseline schema file {0}".format(v1_schema_file)
    except ValueError:
        print "ERROR: File is not proper JSON {0}".format(v1_schema_file)

    v2_schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v2/baselines.spec.json')
    try:
        v2_schema = json.loads(open(v2_schema_file, 'rb').read())
    except IOError:
        print "ERROR: reading version 2 baseline schema file {0}".format(v2_schema_file)
    except ValueError:
        print "ERROR: File is not proper JSON {0}".format(v2_schema_file)

    error = False
    baselines_manifest_files = path.join(path.expanduser(REPO_PATH), "baselines/*.yml")

    for baselines_manifest_file in glob.glob(baselines_manifest_files):
        if verbose:
            print "processing baseline {0}".format(baselines_manifest_file)

        # read in each baseline
        with open(baselines_manifest_file, 'r') as stream:
            try:
                baseline = list(yaml.safe_load_all(stream))[0]
            except yaml.YAMLError as exc:
                print(exc)
                print "Error reading {0}".format(baselines_manifest_file)
                error = True
                continue

        # validate v1 and v2 stories against spec
        if baseline['spec_version'] == 1:
            try:
                jsonschema.validate(instance=baseline, schema=v1_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), baselines_manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True

        elif baseline['spec_version'] == 2:
            try:
                jsonschema.validate(instance=baseline, schema=v2_schema)
            except jsonschema.exceptions.ValidationError as json_ve:
                print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), baselines_manifest_file)
                print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
                error = True

        else:
            print "ERROR: Baseline {0} does not contain a spec_version which is required".format(baselines_manifest_file)
            error = True
            continue

        # now lets validate the content
        baselines_errors = validate_baselines_content(baseline, BASELINE_UUIDS, macros, lookups)
        if baselines_errors:
            error = True
            for err in baselines_errors:
                print "{0} at:\n\t {1}".format(err, baselines_manifest_file)

    return error


def validate_macros(REPO_PATH, verbose):
    ''' Validates Macros'''
    error = False

    schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v2/macros.spec.json')
    schema = json.loads(open(schema_file, 'rb').read())

    macro_manifests = {}
    macros_manifest_files = path.join(path.expanduser(REPO_PATH), "macros/*.yml")
    for macros_manifest_file in glob.glob(macros_manifest_files):
        if verbose:
            print "processing macro {0}".format(macros_manifest_file)

        # read in each macro
        with open(macros_manifest_file, 'r') as stream:
            try:
                macro = list(yaml.safe_load_all(stream))[0]
            except yaml.YAMLError as exc:
                print(exc)
                print "Error reading {0}".format(macros_manifest_file)
                error = True
                continue


        try:
            jsonschema.validate(instance=macro, schema=schema)
        except jsonschema.exceptions.ValidationError as json_ve:
            print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), macros_manifest_file)
            print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
            error = True

        macro_manifests[macro['name']] = macro

    return error, macro_manifests

def validate_lookups(REPO_PATH, verbose):
    ''' Validates Lookups'''
    error = False

    schema_file = path.join(path.expanduser(REPO_PATH), 'spec/v2/lookups.spec.json')
    schema = json.loads(open(schema_file, 'rb').read())

    lookup_manifests = {}
    lookups_manifest_files = path.join(path.expanduser(REPO_PATH), "lookups/*.yml")
    for lookups_manifest_file in glob.glob(lookups_manifest_files):
        if verbose:
            print "processing lookup {0}".format(lookups_manifest_file)

        # read in each lookup
        with open(lookups_manifest_file, 'r') as stream:
            try:
                lookup = list(yaml.safe_load_all(stream))[0]
            except yaml.YAMLError as exc:
                print(exc)
                print "Error reading {0}".format(lookups_manifest_file)
                error = True
                continue

        try:
            jsonschema.validate(instance=lookup, schema=schema)
        except jsonschema.exceptions.ValidationError as json_ve:
            print "ERROR: {0} at:\n\t{1}".format(json.dumps(json_ve.message), lookups_manifest_file)
            print "\tAffected Object: {}".format(json.dumps(json_ve.instance))
            error = True


        if 'filename' in lookup:
            lookup_csv_file = path.join(path.expanduser(REPO_PATH), "lookups/%s" % lookup['filename'])
            if not path.isfile(lookup_csv_file):
                print "ERROR: filename {} does not exist".format(lookup['filename'])
                print lookup_csv_file
                print "\t{}".format(lookups_manifest_file)
                error = True

        lookup_manifests[lookup['name']] = lookup

    return error, lookup_manifests


if __name__ == "__main__":
    # grab arguments
    parser = argparse.ArgumentParser(description="validates security content manifest files", epilog="""
        Validates security manifest for correctness, adhering to spec and other common items.
        VALIDATE DOES NOT PROCESS RESPONSES SPEC for the moment.""")
    parser.add_argument("-p", "--path", required=True, help="path to security-security content repo")
    parser.add_argument("-v", "--verbose", required=False, action='store_true', help="prints verbose output")
    # parse them
    args = parser.parse_args()
    REPO_PATH = args.path
    verbose = args.verbose

    macros_error, macros = validate_macros(REPO_PATH, verbose)

    lookups_error, lookups = validate_lookups(REPO_PATH, verbose)

    story_error = validate_story(REPO_PATH, verbose)

    detection_error = validate_detection(REPO_PATH, verbose, macros, lookups)

    investigation_error = validate_investigation(REPO_PATH, verbose, macros, lookups)

    baseline_error = validate_baselines(REPO_PATH, verbose, macros, lookups)


    if story_error:
        sys.exit("Errors found")
    elif detection_error:
        sys.exit("Errors found")
    elif investigation_error:
        sys.exit("Errors found")
    elif baseline_error:
        sys.exit("Errors found")
    elif macros_error:
        sys.exit("Errors found")
    elif lookups_error:
        sys.exit("Errors found")
    else:
        print "No Errors found"
