HEADER_PREFIX_KEY = 'header_prefix'
METADATA_PREFIX_KEY = 'metadata_prefix'

AWS_HEADER_PREFIX = 'x-amz-'

ACL_HEADER_KEY = 'acl-header'
AUTH_HEADER_KEY = 'auth-header'
COPY_SOURCE_HEADER_KEY = 'copy-source-header'
COPY_SOURCE_VERSION_ID_HEADER_KEY = 'copy-source-version-id-header'
COPY_SOURCE_RANGE_HEADER_KEY = 'copy-source-range-header'
DELETE_MARKER_HEADER_KEY = 'delete-marker-header'
DATE_HEADER_KEY = 'date-header'
METADATA_DIRECTIVE_HEADER_KEY = 'metadata-directive-header'
RESUMABLE_UPLOAD_HEADER_KEY = 'resumable-upload-header'
SECURITY_TOKEN_HEADER_KEY = 'security-token-header'
STORAGE_CLASS_HEADER_KEY = 'storage-class'
MFA_HEADER_KEY = 'mfa-header'
SERVER_SIDE_ENCRYPTION_KEY = 'server-side-encryption-header'
VERSION_ID_HEADER_KEY = 'version-id-header'
RESTORE_HEADER_KEY = 'restore-header'


HeaderInfoMap = {
    HEADER_PREFIX_KEY: AWS_HEADER_PREFIX,
    METADATA_PREFIX_KEY: AWS_HEADER_PREFIX + 'meta-',
    ACL_HEADER_KEY: AWS_HEADER_PREFIX + 'acl',
    AUTH_HEADER_KEY: 'AWS',
    COPY_SOURCE_HEADER_KEY: AWS_HEADER_PREFIX + 'copy-source',
    COPY_SOURCE_VERSION_ID_HEADER_KEY: AWS_HEADER_PREFIX +
                                       'copy-source-version-id',
    COPY_SOURCE_RANGE_HEADER_KEY: AWS_HEADER_PREFIX + 'copy-source-range',
    DATE_HEADER_KEY: AWS_HEADER_PREFIX + 'date',
    DELETE_MARKER_HEADER_KEY: AWS_HEADER_PREFIX + 'delete-marker',
    METADATA_DIRECTIVE_HEADER_KEY: AWS_HEADER_PREFIX +
                                   'metadata-directive',
    RESUMABLE_UPLOAD_HEADER_KEY: None,
    SECURITY_TOKEN_HEADER_KEY: AWS_HEADER_PREFIX + 'security-token',
    SERVER_SIDE_ENCRYPTION_KEY: AWS_HEADER_PREFIX +
                                'server-side-encryption',
    VERSION_ID_HEADER_KEY: AWS_HEADER_PREFIX + 'version-id',
    STORAGE_CLASS_HEADER_KEY: AWS_HEADER_PREFIX + 'storage-class',
    MFA_HEADER_KEY: AWS_HEADER_PREFIX + 'mfa',
    RESTORE_HEADER_KEY: AWS_HEADER_PREFIX + 'restore',
}