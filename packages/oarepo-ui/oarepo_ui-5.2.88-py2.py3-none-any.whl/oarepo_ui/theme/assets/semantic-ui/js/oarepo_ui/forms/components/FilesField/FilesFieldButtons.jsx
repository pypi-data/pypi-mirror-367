import React, { useState } from "react";
import PropTypes from "prop-types";
import { Button, Icon } from "semantic-ui-react";
import { FileEditWrapper, FileUploadWrapper } from "./FilesFieldWrappers";
import { useDepositFileApiClient } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_ui/i18next";

let LOCALE;

if (i18next.language === "cs") {
  LOCALE = "cs_CZ";
} else if (i18next.language === "en") {
  LOCALE = "en_US";
} else {
  LOCALE = i18next.language;
}

export const EditFileButton = ({ fileName, record, allowedFileTypes }) => {
  return (
    <FileEditWrapper
      props={{
        config: { record: record },
        autoExtractImagesFromPDFs: false,
        locale: LOCALE,
        startEvent: { event: "edit-file", data: { file_key: fileName } },
        modifyExistingFiles: true,
        allowedFileTypes: allowedFileTypes,
      }}
    />
  );
};

EditFileButton.propTypes = {
  fileName: PropTypes.string.isRequired,
  record: PropTypes.object.isRequired,
  allowedFileTypes: PropTypes.array,
};

export const UploadFileButton = ({
  record,
  handleFilesUpload,
  allowedFileTypes,
  fileMetadataFields,
  required,
}) => {
  return (
    <FileUploadWrapper
      props={{
        config: { record: record },
        autoExtractImagesFromPDFs: false,
        locale: LOCALE,
        allowedFileTypes: allowedFileTypes,
        startEvent: null,
        onCompletedUpload: (result) => {
          handleFilesUpload();
        },
        allowedMetaFields: fileMetadataFields,
      }}
      required={required}
    />
  );
};

UploadFileButton.propTypes = {
  record: PropTypes.object.isRequired,
  handleFilesUpload: PropTypes.func.isRequired,
  allowedFileTypes: PropTypes.array,
  required: PropTypes.bool,
  fileMetadataFields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      defaultValue: PropTypes.string,
      isUserInput: PropTypes.bool.isRequired,
    })
  ),
};

export const DeleteFileButton = ({ file, handleFileDeletion }) => {
  const { _delete } = useDepositFileApiClient();
  const [isDeleting, setIsDeleting] = useState(false);
  const handleDelete = async () => {
    setIsDeleting(true);
    _delete(file)
      .then((response) => {
        setIsDeleting(false);
        if (response.status === 204) handleFileDeletion(file);
      })
      .catch((error) => {
        setIsDeleting(false);
      });
  };
  return isDeleting ? (
    <Icon loading name="spinner" />
  ) : (
    <Button
      disabled={isDeleting}
      className="transparent"
      type="button"
      onClick={handleDelete}
      aria-label={i18next.t("Delete file")}
    >
      <Icon aria-hidden="true" name="trash alternate" className="m-0" />
    </Button>
  );
};

DeleteFileButton.propTypes = {
  file: PropTypes.object.isRequired,
  handleFileDeletion: PropTypes.func.isRequired,
};
