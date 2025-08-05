import asyncio
from copy import copy
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from zalo_bot import request
from zalo_bot._files.input_media import InputMedia, InputPaidMedia
from zalo_bot._update import Update
from zalo_bot._utils.default_value import DEFAULT_NONE, DefaultValue
from zalo_bot._utils.logging import get_logger
from zalo_bot._utils.types import JSONDict, ODVInput
from zalo_bot._webhook import Webhook
from zalo_bot._zalo_object import ZaloObject
from zalo_bot._user import User
from zalo_bot.constants import BASE_URL
from zalo_bot.error import InvalidToken
from zalo_bot.request._base_request import BaseRequest
from zalo_bot.request._httpx_request import HTTPXRequest
from zalo_bot.request._request_data import RequestData
from zalo_bot.request._request_parameter import RequestParameter
from zalo_bot.warnings import PTBDeprecationWarning
from zalo_bot._message import Message


BT = TypeVar("BT", bound="Bot")


class Bot(ZaloObject, AsyncContextManager["Bot"]):
    _LOGGER = get_logger(__name__)

    __slots__ = (
        "_base_url",
        "_request",
        "_token",
        "_initialized",
    )

    def __init__(self, token: str, base_url: str = BASE_URL) -> None:
        super().__init__(api_kwargs=None)
        if not token:
            raise InvalidToken(
                "You must pass the token you received from https://bot.zapps.vn/docs/create-bot/"
            )
        if not base_url:
            base_url = BASE_URL

        self._token = token
        self._base_url: str = f"{base_url}/bot{self._token}"

        self._request: Tuple[BaseRequest, BaseRequest] = (
            HTTPXRequest(),
            HTTPXRequest(),
        )
        self._initialized: bool = False

    def _insert_defaults(self, data: Dict[str, object]) -> None:
        """Make ext.Defaults work by converting DefaultValue instances to normal values.

        This is necessary because shortcuts like Message.reply_text need to work for both
        Bot and ExtBot, so they have DEFAULT_NONE default values.
        """
        # Set correct parse_mode for InputMedia objects and replace DefaultValue instances
        for key, val in data.items():
            if isinstance(val, InputMedia):
                # Copy object to avoid editing in-place
                new = copy.copy(val)
                with new._unfrozen():
                    new.parse_mode = DefaultValue.get_value(new.parse_mode)
                data[key] = new
            elif (
                key == "media"
                and isinstance(val, Sequence)
                and not isinstance(val[0], InputPaidMedia)
            ):
                # Copy objects to avoid editing in-place
                copy_list = [copy.copy(media) for media in val]
                for media in copy_list:
                    with media._unfrozen():
                        media.parse_mode = DefaultValue.get_value(media.parse_mode)
                data[key] = copy_list
            else:
                data[key] = DefaultValue.get_value(val)

    async def get_me(
        self,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> User:
        """A simple method for testing your bot's auth token. Requires no parameters.

        Returns:
            :class:`zalo_bot.User`: A :class:`zalo_bot.User` instance representing that bot if the
            credentials are valid, :obj:`None` otherwise.

        Raises:
            :class:`zalo_bot.error.ZaloError`

        """
        result = await self._post(
            "getMe",
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        self._bot_user = User.de_json(result, self)
        return self._bot_user  # type: ignore[return-value]

    async def get_update(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,  # noqa: ASYNC109
        allowed_updates: Optional[Sequence[str]] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Update:
        """Receive incoming updates using long polling.

        Note:
            1. This method will not work if an outgoing webhook is set up.
            2. In order to avoid getting duplicate updates, recalculate offset after each
               server response.
            3. To take full advantage of this library take a look at :class:`zalo_bot.ext.Updater`

        .. seealso:: :meth:`zalo_bot.ext.Application.run_polling`,
            :meth:`zalo_bot.ext.Updater.start_polling`

        Args:
            offset (:obj:`int`, optional): Identifier of the first update to be returned. Must be
                greater by one than the highest among the identifiers of previously received
                updates. By default, updates starting with the earliest unconfirmed update are
                returned. An update is considered confirmed as soon as this method is called with
                an offset higher than its :attr:`zalo_bot.Update.update_id`. The negative offset
                can be specified to retrieve updates starting from -offset update from the end of
                the updates queue. All previous updates will be forgotten.
            limit (:obj:`int`, optional): Limits the number of updates to be retrieved. Values
                between :tg-const:`zalo_bot.constants.PollingLimit.MIN_LIMIT`-
                :tg-const:`zalo_bot.constants.PollingLimit.MAX_LIMIT` are accepted.
                Defaults to ``100``.
            timeout (:obj:`int`, optional): Timeout in seconds for long polling. Defaults to ``0``,
                i.e. usual short polling. Should be positive, short polling should be used for
                testing purposes only.


        Returns:
            :class:`zalo_bot.Update`: An object representing the updates.

        Raises:
            :class:`zalo_bot.error.ZaloError`

        """
        data: JSONDict = {
            "timeout": timeout,
            "offset": offset,
            "limit": limit,
            "allowed_updates": allowed_updates,
        }

        # Handle None read_timeout case
        if not isinstance(read_timeout, DefaultValue):
            arg_read_timeout: float = read_timeout or 0
        else:
            try:
                arg_read_timeout = self._request[0].read_timeout or 0
            except NotImplementedError:
                arg_read_timeout = 2
                self._warn(
                    PTBDeprecationWarning(
                        "20.7",
                        f"The class {self._request[0].__class__.__name__} does not override "
                        "the property `read_timeout`. Overriding this property will be mandatory "
                        "in future versions. Using 2 seconds as fallback.",
                    ),
                    stacklevel=2,
                )

        # Ideally we'd use an aggressive read timeout for the polling. However,
        # * Short polling should return within 2 seconds.
        # * Long polling poses a different problem: the connection might have been dropped while
        #   waiting for the server to return and there's no way of knowing the connection had been
        #   dropped in real time.
        result = cast(
            JSONDict,
            await self._post(
                "getUpdates",
                data,
                read_timeout=arg_read_timeout + timeout if timeout else arg_read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
                api_kwargs=api_kwargs,
            ),
        )

        # If the result is empty, we return an empty list
        if result:
            self._LOGGER.debug("Getting update: %s", result.get("event_name"))
        else:
            self._LOGGER.debug("No new updates found.")

        try:
            return Update.de_json(result, self)
        except Exception as exc:
            # This logging is in place mostly b/c we can't access the raw json data in Updater,
            # where the exception is caught and logged again. Still, it might also be beneficial
            # for custom usages of `get_update`.
            self._LOGGER.critical(
                "Error while parsing updates! Received data was %r", result, exc_info=exc
            )
            raise

    async def _post(
        self,
        endpoint: str,
        data: Optional[JSONDict] = None,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> Any:
        # Return type is Union[bool, JSONDict, List[JSONDict]], but hard to tell mypy
        # which methods expect which return values, so use Any to avoid type: ignore
        if data is None:
            data = {}

        # Insert defaults for ext.Defaults compatibility
        self._insert_defaults(data)

        # Insert api_kwargs in-place
        if api_kwargs:
            data.update(api_kwargs)

        # Insert is in-place, so no return value for data
        self._insert_defaults(data)

        # Drop any None values because Zalo Bot doesn't handle them well
        data = {key: value for key, value in data.items() if value is not None}

        return await self._do_post(
            endpoint=endpoint,
            data=data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )

    async def _do_post(
        self,
        endpoint: str,
        data: JSONDict,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> Union[bool, JSONDict, List[JSONDict]]:
        # This also converts datetimes into timestamps.
        # We don't do this earlier so that _insert_defaults (see above) has a chance to convert
        # to the default timezone in case this is called by ExtBot
        request_data = RequestData(
            parameters=[
                RequestParameter.from_input(key, value) for key, value in data.items()
            ],
        )

        request = self._request[0] if endpoint == "getUpdates" else self._request[1]

        self._LOGGER.debug(
            "Calling Bot API endpoint `%s` with parameters `%s`", endpoint, data
        )

        result = await request.post(
            url=f"{self._base_url}/{endpoint}",
            request_data=request_data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
        )
        self._LOGGER.debug(
            "Call to Bot API endpoint `%s` finished with return value `%s`",
            endpoint,
            result,
        )

        return result

    async def initialize(self) -> None:
        """Initialize resources used by this class. Currently calls :meth:`get_me` to
        cache :attr:`bot` and calls :meth:`zalo_bot.request.BaseRequest.initialize` for
        the request objects used by this bot.

        .. seealso:: :meth:`shutdown`
        """
        if self._initialized:
            self._LOGGER.debug("This Bot is already initialized.")
            return

        await asyncio.gather(
            self._request[0].initialize(), self._request[1].initialize()
        )
        # Since the bot is to be initialized only once, we can also use it for
        # verifying the token passed and raising an exception if it's invalid.
        try:
            await self.get_me()
        except InvalidToken as exc:
            raise InvalidToken(
                f"The token `{self._token}` was rejected by the server."
            ) from exc
        self._initialized = True

    async def shutdown(self) -> None:
        """Stop & clear resources used by this class. Currently just calls
        :meth:`zalo_bot.request.BaseRequest.shutdown` for the request objects used by this bot.

        .. seealso:: :meth:`initialize`

        """
        if not self._initialized:
            self._LOGGER.debug("This Bot is already shut down. Returning.")
            return

        await asyncio.gather(self._request[0].shutdown(), self._request[1].shutdown())
        self._initialized = False

    async def __aenter__(self: BT) -> BT:
        """
        |async_context_manager| :meth:`initializes <initialize>` the Bot.

        Returns:
            The initialized Bot instance.

        Raises:
            :exc:`Exception`: If an exception is raised during initialization, :meth:`shutdown`
                is called in this case.
        """
        try:
            await self.initialize()
        except Exception:
            await self.shutdown()
            raise
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Shut down the bot."""
        await self.shutdown()
        # Don't return True so exceptions are not suppressed
        # https://docs.python.org/3/reference/datamodel.html?#object.__aexit__

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to_message_id: str = None,
    ) -> Message:
        """
        Send a simple text message to a chat.
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "text": text,
        }

        return await self._send_message(
            "sendMessage", data, reply_to_message_id=reply_to_message_id
        )

    async def _send_message(
        self,
        endpoint: str,
        data: JSONDict,
        *,
        reply_to_message_id: str = None,
    ) -> Message:
        """
        Send data to the API and return the Message object.
        """
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id

        result = await self._post(endpoint, data)
        return Message.de_json(result, self)

    async def _set_webhook_async(self, url: str, secret_token: str) -> bool:
        """Internal async helper to set webhook."""
        result = await self._post("setWebhook", {"url": url, "secret_token": secret_token})
        return bool(result)

    def set_webhook(self, url: str, secret_token: str) -> bool:
        """Configure a webhook URL synchronously."""
        return asyncio.run(self._set_webhook_async(url, secret_token))

    async def _delete_webhook_async(self) -> bool:
        """Delete webhook URL synchronously."""
        result = await self._post("deleteWebhook")
        return bool(result)
    
    def delete_webhook(self) -> bool:
        """Delete the webhook URL synchronously."""
        return asyncio.run(self._delete_webhook_async())
    
    async def _get_webhook_info_async(self) -> Webhook:
        """Get webhook information asynchronously."""
        result = await self._post("getWebhookInfo")
        return Webhook.de_json(result, self)
    
    def get_webhook_info(self) -> Webhook:
        """Get webhook information synchronously."""
        return asyncio.run(self._get_webhook_info_async())
    
    async def send_photo(
        self,
        chat_id: str,
        caption: str,
        photo: str,
        *,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        """
        Send a photo to a chat.
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
        }

        return await self._send_message(
            "sendPhoto", data, reply_to_message_id=reply_to_message_id
        )
    
    async def send_sticker(
        self,
        chat_id: str,
        sticker: str,
        *,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        """
        Send a sticker to a chat.
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "sticker": sticker,
        }

        return await self._send_message(
            "sendSticker", data, reply_to_message_id=reply_to_message_id
        )

    async def send_chat_action(
        self,
        chat_id: Union[int, str],
        action: str,
        *,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
        api_kwargs: Optional[JSONDict] = None,
    ) -> bool:
        """
        Send chat action.
        
        Use this method when you need to tell the user that something is happening on the bot's
        side. The status is set for 5 seconds or less (when a message arrives from your bot,
        Zalo Bot clients clear its typing status).
        
        Args:
            chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or username
                of the target channel (in the format ``@channelusername``).
            action (:obj:`str`): Type of action to broadcast. Choose one, depending on what the
                user is about to receive: ``typing`` for text messages, ``upload_photo`` for
                photos, ``record_video`` or ``upload_video`` for videos, ``record_voice`` or
                ``upload_voice`` for voice notes, ``upload_document`` for general files,
                ``choose_sticker`` for stickers, ``find_location`` for location data,
                ``record_video_note`` or ``upload_video_note`` for video notes.
            read_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`BaseRequest.post.read_timeout`. Defaults to ``DEFAULT_NONE``.
            write_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`BaseRequest.post.write_timeout`. Defaults to ``DEFAULT_NONE``.
            connect_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`BaseRequest.post.connect_timeout`. Defaults to ``DEFAULT_NONE``.
            pool_timeout (:obj:`float` | :obj:`None`, optional): Value to pass to
                :paramref:`BaseRequest.post.pool_timeout`. Defaults to ``DEFAULT_NONE``.
            api_kwargs (:obj:`dict`, optional): Arbitrary keyword arguments to be passed to the
                Zalo Bot API.
                
        Returns:
            :obj:`bool`: On success, ``True`` is returned.
            
        Raises:
            :class:`zalo_bot.error.ZaloError`
        """
        data: JSONDict = {
            "chat_id": chat_id,
            "action": action,
        }

        result = await self._post(
            "sendChatAction",
            data,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            connect_timeout=connect_timeout,
            pool_timeout=pool_timeout,
            api_kwargs=api_kwargs,
        )
        return result  # type: ignore[return-value]
