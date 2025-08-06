import asyncio
from pathlib import Path

from src.inopyutils import InoFileHelper


async def main():
    result = await InoFileHelper.validate_files(
        input_path=Path(r"E:\NIL\spark\python\InoFacefusion\.jobs2\3"),
        include_image=True,
        include_video=False
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
