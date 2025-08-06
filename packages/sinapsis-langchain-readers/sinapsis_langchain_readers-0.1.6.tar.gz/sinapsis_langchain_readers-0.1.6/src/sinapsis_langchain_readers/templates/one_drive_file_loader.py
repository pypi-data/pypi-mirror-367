# -*- coding: utf-8 -*-
from langchain_community.document_loaders import OneDriveFileLoader
from O365 import Account
from O365.drive import File
from sinapsis_core.template_base import (
    TemplateAttributes,
    TemplateAttributeType,
)

from sinapsis_langchain_readers.templates.base_static_loader import BaseStaticLoader


class LangChainOneDriveFileLoader(BaseStaticLoader):
    """
    Template to load documents using Langchain OneDriveFileLoader module.
    The template loads a OneDrive file either as a Document object in the generic_data field
    of DataContainer of each string as a TextPacket if add_document_as_text_packet is set as True
    Instructions reference: https://python.langchain.com/docs/integrations/document_loaders/microsoft_onedrive/

    Prerequisites
    *Configure an Microsoft Entra app:
        https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
    *Configure a client secret
    *Add 'offline_access' and 'Files.Read.All' to the app scopes:
        https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-configure-app-expose-web-apis
    *Find out your Drive ID by making a query and finding the 'id' field at
        https://developer.microsoft.com/en-us/graph/graph-explorer
    *Add the Entra client ID to 'O365_CLIENT_ID' environment variable
    *Add the client secret value to 'O365_CLIENT_SECRET' environment variable
    *Add your Drive ID to the config attributes

    Usage
    *Add the information to query through 'file_path' or 'file_id' in the config
    *The first time OneDriveFileLoader is run, it will give a URL to visit. Follow the link and
        copy the URL of the site that appears after consenting to permissions.
    *This will save a token at ~/.credentials/o365_token.txt
    *After this, modify 'auth_with_token' attribute to True and add the 'token_path'

    Usage example:

    agent:
    name: one_drive_file_loader
    description: "One Drive File Loader example"

    templates:

    - template_name: InputTemplate
    class_name: InputTemplate
    attributes: {}

    - template_name: LangChainOneDriveFileLoader
    class_name: LangChainOneDriveFileLoader
    template_input: InputTemplate
    attributes:
        add_document_as_text_packet: false
        file_path: "/path/to/file.pdf"
        file_id: "file_id_from_onedrive"
        drive_id: drive_id
        auth_with_token: false
        token_path: /path/to/token.txt
    """

    class AttributesBaseModel(TemplateAttributes):
        """
        add_document_as_text_packet(bool): Whether to add document as text packet or not.
        file_path(str): Path to the file in OneDrive (alternative to file_id).
        file_id(str): ID of the file in OneDrive (alternative to file_path).
        drive_id(str): The OneDrive drive ID.
        auth_with_token(bool): Whether to authenticate with a saved token.
        token_path(str): Path to the saved authentication token.
        """

        add_document_as_text_packet: bool = False
        file_path: str | None = None
        file_id: str | None = None
        drive_id: str
        auth_with_token: bool = False
        token_path: str = "/home/runner/.credentials/o365_token.txt"

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initialize OneDriveFileLoader with validated File object.

        Creates an authenticated connection to OneDrive, retrieves the specified file,
        validates it's actually a file (not a folder), and initializes the
        OneDriveFileLoader with the File object.

        Args:
            attributes (TemplateAttributeType): Configuration attributes containing
                OneDrive connection details and file identification parameters.

        Raises:
            ValueError: If the specified item is a folder instead of a file.
            FileNotFoundError: If the specified file_id or file_path doesn't exist.
            RuntimeError: If authentication with OneDrive fails.
            ImportError: If O365 package is not installed.
        """
        super().__init__(attributes)
        file_obj = self._get_file_object()
        self.loader = OneDriveFileLoader(file=file_obj)

    def _get_authenticated_account(self) -> Account:
        """
        Handles both token-based authentication (using saved tokens) and
        interactive authentication flow.

        Returns:
            Account: Authenticated O365 Account instance ready for API calls.
        """
        account = Account(credentials=())
        if self.attributes.auth_with_token:
            account.authenticate(token_path=self.attributes.token_path)
        else:
            account.authenticate()
        return account

    def _get_file_from_drive(self, account: Account) -> File:
        """
        Connects to the specified OneDrive and retrieves the file using either
        file_id or file_path. Validates that the returned object is actually a
        file and not a folder, as OneDriveFileLoader only supports file objects.

        Args:
            account (Account): Authenticated O365 Account instance.

        Returns:
            File: O365 File object compatible with OneDriveFileLoader. This includes
                File, Image, and Photo objects (all inherit from File class).

        Raises:
            ValueError: If the specified item is not a File compatible object.
                This occurs when:
                - The item is a Folder (folders cannot be processed by OneDriveFileLoader)
        """
        drive = account.storage().get_drive(self.attributes.drive_id)

        if self.attributes.file_id:
            file_obj = drive.get_item(self.attributes.file_id)
        else:
            file_obj = drive.get_item_by_path(self.attributes.file_path)

        if not file_obj.is_file:
            raise ValueError("The specified item is not a File compatible with O365.drive.File.")

        return file_obj

    def _get_file_object(self) -> File:
        """
        Orchestrates the full process of authentication and file retrieval.
        This is the main method that combines authentication and file loading
        to provide a File object ready for use with OneDriveFileLoader.

        Returns:
            File: Validated O365 File object that can be used by OneDriveFileLoader
                to download and process the document content.
        """
        account = self._get_authenticated_account()
        return self._get_file_from_drive(account)
