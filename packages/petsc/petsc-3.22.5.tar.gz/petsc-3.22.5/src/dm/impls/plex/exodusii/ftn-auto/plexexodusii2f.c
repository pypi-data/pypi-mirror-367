#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexexodusii2.c */
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

#include "petscdmplex.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiisetzonalvariable_ PETSCVIEWEREXODUSIISETZONALVARIABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiisetzonalvariable_ petscviewerexodusiisetzonalvariable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiisetnodalvariable_ PETSCVIEWEREXODUSIISETNODALVARIABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiisetnodalvariable_ petscviewerexodusiisetnodalvariable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetzonalvariable_ PETSCVIEWEREXODUSIIGETZONALVARIABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetzonalvariable_ petscviewerexodusiigetzonalvariable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetnodalvariable_ PETSCVIEWEREXODUSIIGETNODALVARIABLE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetnodalvariable_ petscviewerexodusiigetnodalvariable
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiisetzonalvariablename_ PETSCVIEWEREXODUSIISETZONALVARIABLENAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiisetzonalvariablename_ petscviewerexodusiisetzonalvariablename
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiisetnodalvariablename_ PETSCVIEWEREXODUSIISETNODALVARIABLENAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiisetnodalvariablename_ petscviewerexodusiisetnodalvariablename
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetzonalvariablename_ PETSCVIEWEREXODUSIIGETZONALVARIABLENAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetzonalvariablename_ petscviewerexodusiigetzonalvariablename
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetnodalvariablename_ PETSCVIEWEREXODUSIIGETNODALVARIABLENAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetnodalvariablename_ petscviewerexodusiigetnodalvariablename
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetnodalvariableindex_ PETSCVIEWEREXODUSIIGETNODALVARIABLEINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetnodalvariableindex_ petscviewerexodusiigetnodalvariableindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetzonalvariableindex_ PETSCVIEWEREXODUSIIGETZONALVARIABLEINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetzonalvariableindex_ petscviewerexodusiigetzonalvariableindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetid_ PETSCVIEWEREXODUSIIGETID
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetid_ petscviewerexodusiigetid
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiisetorder_ PETSCVIEWEREXODUSIISETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiisetorder_ petscviewerexodusiisetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiigetorder_ PETSCVIEWEREXODUSIIGETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiigetorder_ petscviewerexodusiigetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscviewerexodusiiopen_ PETSCVIEWEREXODUSIIOPEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscviewerexodusiiopen_ petscviewerexodusiiopen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateexodus_ DMPLEXCREATEEXODUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateexodus_ dmplexcreateexodus
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscviewerexodusiisetzonalvariable_(PetscViewer viewer,PetscExodusIIInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIISetZonalVariable(PetscPatchDefaultViewers((PetscViewer*)viewer),*num);
}
PETSC_EXTERN void  petscviewerexodusiisetnodalvariable_(PetscViewer viewer,PetscExodusIIInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIISetNodalVariable(PetscPatchDefaultViewers((PetscViewer*)viewer),*num);
}
PETSC_EXTERN void  petscviewerexodusiigetzonalvariable_(PetscViewer viewer,PetscExodusIIInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIIGetZonalVariable(PetscPatchDefaultViewers((PetscViewer*)viewer),num);
}
PETSC_EXTERN void  petscviewerexodusiigetnodalvariable_(PetscViewer viewer,PetscExodusIIInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIIGetNodalVariable(PetscPatchDefaultViewers((PetscViewer*)viewer),num);
}
PETSC_EXTERN void  petscviewerexodusiisetzonalvariablename_(PetscViewer viewer,PetscExodusIIInt *idx, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerExodusIISetZonalVariableName(PetscPatchDefaultViewers((PetscViewer*)viewer),*idx,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewerexodusiisetnodalvariablename_(PetscViewer viewer,PetscExodusIIInt *idx, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerExodusIISetNodalVariableName(PetscPatchDefaultViewers((PetscViewer*)viewer),*idx,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewerexodusiigetzonalvariablename_(PetscViewer viewer,PetscExodusIIInt *idx, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIIGetZonalVariableName(PetscPatchDefaultViewers((PetscViewer*)viewer),*idx,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscviewerexodusiigetnodalvariablename_(PetscViewer viewer,PetscExodusIIInt *idx, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIIGetNodalVariableName(PetscPatchDefaultViewers((PetscViewer*)viewer),*idx,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscviewerexodusiigetnodalvariableindex_(PetscViewer viewer, char name[],PetscExodusIIInt *varIndex, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerExodusIIGetNodalVariableIndex(PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0,varIndex);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewerexodusiigetzonalvariableindex_(PetscViewer viewer, char name[],int *varIndex, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(viewer);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerExodusIIGetZonalVariableIndex(PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0,varIndex);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscviewerexodusiigetid_(PetscViewer viewer,PetscExodusIIInt *exoid, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIIGetId(PetscPatchDefaultViewers((PetscViewer*)viewer),exoid);
}
PETSC_EXTERN void  petscviewerexodusiisetorder_(PetscViewer viewer,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscViewerExodusIISetOrder(PetscPatchDefaultViewers((PetscViewer*)viewer),*order);
}
PETSC_EXTERN void  petscviewerexodusiigetorder_(PetscViewer viewer,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLINTEGER(order);
*ierr = PetscViewerExodusIIGetOrder(PetscPatchDefaultViewers((PetscViewer*)viewer),order);
}
PETSC_EXTERN void  petscviewerexodusiiopen_(MPI_Fint * comm, char name[],PetscFileMode *mode,PetscViewer *exo, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool exo_null = !*(void**) exo ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(exo);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscViewerExodusIIOpen(
	MPI_Comm_f2c(*(comm)),_cltmp0,*mode,exo);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! exo_null && !*(void**) exo) * (void **) exo = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateexodus_(MPI_Fint * comm,PetscExodusIIInt *exoid,PetscBool *interpolate,DM *dm, int *ierr)
{
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexCreateExodus(
	MPI_Comm_f2c(*(comm)),*exoid,*interpolate,dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
