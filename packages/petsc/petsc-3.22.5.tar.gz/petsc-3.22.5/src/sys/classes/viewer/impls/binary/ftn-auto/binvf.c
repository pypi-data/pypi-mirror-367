#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* binv.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscviewer.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarysetusempiio_ PETSCVIEWERBINARYSETUSEMPIIO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarysetusempiio_ petscviewerbinarysetusempiio
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarygetusempiio_ PETSCVIEWERBINARYGETUSEMPIIO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarygetusempiio_ petscviewerbinarygetusempiio
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarysetflowcontrol_ PETSCVIEWERBINARYSETFLOWCONTROL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarysetflowcontrol_ petscviewerbinarysetflowcontrol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarygetflowcontrol_ PETSCVIEWERBINARYGETFLOWCONTROL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarygetflowcontrol_ petscviewerbinarygetflowcontrol
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinaryskipinfo_ PETSCVIEWERBINARYSKIPINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinaryskipinfo_ petscviewerbinaryskipinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarysetskipinfo_ PETSCVIEWERBINARYSETSKIPINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarysetskipinfo_ petscviewerbinarysetskipinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarygetskipinfo_ PETSCVIEWERBINARYGETSKIPINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarygetskipinfo_ petscviewerbinarygetskipinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarysetskipoptions_ PETSCVIEWERBINARYSETSKIPOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarysetskipoptions_ petscviewerbinarysetskipoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarygetskipoptions_ PETSCVIEWERBINARYGETSKIPOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarygetskipoptions_ petscviewerbinarygetskipoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarysetskipheader_ PETSCVIEWERBINARYSETSKIPHEADER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarysetskipheader_ petscviewerbinarysetskipheader
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinarygetskipheader_ PETSCVIEWERBINARYGETSKIPHEADER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinarygetskipheader_ petscviewerbinarygetskipheader
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerbinaryopen_ PETSCVIEWERBINARYOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerbinaryopen_ petscviewerbinaryopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerfilesetmode_ PETSCVIEWERFILESETMODE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerfilesetmode_ petscviewerfilesetmode
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerfilegetmode_ PETSCVIEWERFILEGETMODE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerfilegetmode_ petscviewerfilegetmode
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerbinarysetusempiio_(PetscViewer viewer,PetscBool *use, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinarySetUseMPIIO(PetscPatchDefaultViewers((PetscViewer*)viewer),*use);
}
PETSC_EXTERN void  petscviewerbinarygetusempiio_(PetscViewer viewer,PetscBool *use, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinaryGetUseMPIIO(PetscPatchDefaultViewers((PetscViewer*)viewer),use);
}
PETSC_EXTERN void  petscviewerbinarysetflowcontrol_(PetscViewer viewer,PetscInt *fc, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinarySetFlowControl(PetscPatchDefaultViewers((PetscViewer*)viewer),*fc);
}
PETSC_EXTERN void  petscviewerbinarygetflowcontrol_(PetscViewer viewer,PetscInt *fc, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLINTEGER(fc);
*ierr = PetscViewerBinaryGetFlowControl(PetscPatchDefaultViewers((PetscViewer*)viewer),fc);
}
PETSC_EXTERN void  petscviewerbinaryskipinfo_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinarySkipInfo(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscviewerbinarysetskipinfo_(PetscViewer viewer,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinarySetSkipInfo(PetscPatchDefaultViewers((PetscViewer*)viewer),*skip);
}
PETSC_EXTERN void  petscviewerbinarygetskipinfo_(PetscViewer viewer,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinaryGetSkipInfo(PetscPatchDefaultViewers((PetscViewer*)viewer),skip);
}
PETSC_EXTERN void  petscviewerbinarysetskipoptions_(PetscViewer viewer,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinarySetSkipOptions(PetscPatchDefaultViewers((PetscViewer*)viewer),*skip);
}
PETSC_EXTERN void  petscviewerbinarygetskipoptions_(PetscViewer viewer,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinaryGetSkipOptions(PetscPatchDefaultViewers((PetscViewer*)viewer),skip);
}
PETSC_EXTERN void  petscviewerbinarysetskipheader_(PetscViewer viewer,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinarySetSkipHeader(PetscPatchDefaultViewers((PetscViewer*)viewer),*skip);
}
PETSC_EXTERN void  petscviewerbinarygetskipheader_(PetscViewer viewer,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerBinaryGetSkipHeader(PetscPatchDefaultViewers((PetscViewer*)viewer),skip);
}
PETSC_EXTERN void  petscviewerbinaryopen_(MPI_Fint * comm, char name[],PetscFileMode *mode,PetscViewer *viewer, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool viewer_null = !*(void**) viewer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerBinaryOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,*mode,viewer);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! viewer_null && !*(void**) viewer) * (void **) viewer = (void *)-2;
}
PETSC_EXTERN void  petscviewerfilesetmode_(PetscViewer viewer,PetscFileMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerFileSetMode(PetscPatchDefaultViewers((PetscViewer*)viewer),*mode);
}
PETSC_EXTERN void  petscviewerfilegetmode_(PetscViewer viewer,PetscFileMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerFileGetMode(PetscPatchDefaultViewers((PetscViewer*)viewer),mode);
}
#if defined(__cplusplus)
}
#endif
